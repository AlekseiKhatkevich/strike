import asyncio
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import APIRouter, Depends, Response, WebSocket, WebSocketDisconnect
from fastapi_pagination import LimitOffsetPage
from google._upb._message import MessageMeta
from sqlalchemy import column
from starlette.websockets import WebSocketState

from crud.detentions import zk_daily_stats, zk_for_lawyer
from crud.helpers import create_or_update_with_session_get, delete_via_sql_delete
from internal.constants import WS_FOR_LAWYER_TIME_PERIOD
from internal.dependencies import PBRequestData, PaginParamsDep, SessionDep
from internal.protobuf import pb_from_model_instance
from models import Detention
from serializers.detentions import (
    DetentionDailyStatsOutSerializer,
    JailInSerializer,
    WSActionType,
    WSDataCreateUpdateSerializer,
    WSDataGetDeleteSerializer,
    WSDetentionOutSerializer,
    WSForLawyerInSerializer,
)
from serializers.proto.compiled import jail_pb2

__all__ = (
    'router',
)

router = APIRouter(tags=['detentions'])


JailPBDataDep = Annotated[MessageMeta, Depends(PBRequestData(jail_pb2.Jail, serializer=JailInSerializer))]


@router.post('/')
async def create_jail(session: SessionDep,
                      serializer: JailPBDataDep,
                      ) -> Response:
    """
    ЭП создания новой крытой.
    """
    instance = await create_or_update_with_session_get(
        session,
        'Jail',
        serializer.model_dump(),
    )
    jail_buff = pb_from_model_instance(jail_pb2.Jail, instance)

    return Response(content=jail_buff.SerializeToString(), media_type='application/x-protobuf')


@router.get('/statistics/daily/')
async def daily_stats_ep(session: SessionDep,
                         params: PaginParamsDep,
                         ) -> LimitOffsetPage[DetentionDailyStatsOutSerializer]:
    """
    ЭП отдачи ежедневной статистики.
    """
    col = await zk_daily_stats(session, params)
    out = LimitOffsetPage[DetentionDailyStatsOutSerializer]
    return out.create(col.items, params, total=col.total)


@asynccontextmanager
async def respond_with_exception_if_any(websocket: WebSocket) -> WebSocket:
    """
    В случае получения исключения пересылаем это исключение в виде текста на клиентский ws.
    """
    try:
        yield websocket
    except Exception as err:
        await websocket.send_text(str(err))


@router.websocket('/ws/lawyer')
async def for_lawyer(session: SessionDep, websocket: WebSocket) -> None:
    """
    Отдает все данные о ЗК по переданным условиям фильтрации, затем раз в n секунд
    отдает на фронт новые записи с теми же условиями фильтрации.
    """
    max_id = 1

    async def send_zks_onto_frontend(zks):
        await websocket.send_json(
            [WSDetentionOutSerializer.model_validate(zk).model_dump_json() for zk in zks]
        )
        nonlocal max_id
        max_id = max(max_id, max(zk.id for zk in zks))

    await websocket.accept()

    async with respond_with_exception_if_any(websocket) as websocket:
        data = await websocket.receive_json()
        deserialized_data = WSForLawyerInSerializer(**data)

        try:
            while websocket.application_state == WebSocketState.CONNECTED:
                new_zk = await zk_for_lawyer(
                    session, **deserialized_data.model_dump(), last_id=max_id,
                )
                if new_zk:
                    await send_zks_onto_frontend(new_zk)

                await asyncio.sleep(WS_FOR_LAWYER_TIME_PERIOD)
        except WebSocketDisconnect:
            return None


@router.websocket('/ws')
async def websocket_endpoint(session: SessionDep, websocket: WebSocket):
    """
    CRUD модели DETENTION.
    """
    await websocket.accept()
    while True:
        async with respond_with_exception_if_any(websocket) as websocket:
            data = await websocket.receive_json()
            action = data['action']

            match action:
                case WSActionType.create_detention.value | WSActionType.update_detention.value:
                    instance = await create_or_update_with_session_get(
                        session,
                        'Detention',
                        WSDataCreateUpdateSerializer(**data['data']).model_dump(),
                    )
                    await websocket.send_json(
                        WSDetentionOutSerializer.model_validate(instance).model_dump_json(),
                    )

                case WSActionType.delete_detentions.value:
                    id_to_delete = WSDataGetDeleteSerializer(**data['data']).id
                    deleted_ids = await delete_via_sql_delete(
                        session,
                        'Detention',
                        column('id') == id_to_delete,
                    )
                    await websocket.send_json(deleted_ids)

                case WSActionType.get_detentions.value:
                    id_to_get = WSDataGetDeleteSerializer(**data['data']).id
                    instance = await session.get(Detention, id_to_get)
                    if instance is not None:
                        await websocket.send_json(
                            WSDetentionOutSerializer.model_validate(instance).model_dump_json(),
                        )
                    else:
                        await websocket.send_text(f'Instance with id {id_to_get} has not found.')
