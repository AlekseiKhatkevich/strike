from contextlib import asynccontextmanager

from fastapi import APIRouter, WebSocket
from sqlalchemy import column

from crud.helpers import create_or_update_with_session_get, delete_via_sql_delete
from internal.dependencies import SessionDep
from models import Detention
from serializers.detentions import (
    WSActionType,
    WSDataCreateUpdateSerializer,
    WSDataGetDeleteSerializer,
    WSDetentionOutSerializer,
)

__all__ = (
    'router',
)

router = APIRouter(tags=['detentions'])


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
async def for_lawyer(session: SessionDep, websocket: WebSocket):
    """

    """
    await websocket.accept()
    while True:
        pass#NOTIFY


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
