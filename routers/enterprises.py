from fastapi import APIRouter, Depends, status
from fastapi_pagination import LimitOffsetPage
from sqlalchemy import column

from crud.enterprises import get_enterprises
from crud.helpers import create_or_update_with_session_get, delete_via_sql_delete, get_collection_paginated
from internal.dependencies import GetParamsIdsDep, PaginParamsDep, PathIdDep, SessionDep, jwt_authorize
from serializers.enterprises import EnterpriseInSerializer, EnterpriseOutSerializer

__all__ = (
    'router',
)


router = APIRouter(tags=['enterprises'], dependencies=[Depends(jwt_authorize)])


@router.post('/', status_code=status.HTTP_201_CREATED)
@router.put('/')
async def create_or_update_enterprise_ep(session: SessionDep,
                                         enterprise_data: EnterpriseInSerializer,
                                         ) -> EnterpriseOutSerializer:
    """
    Создание / обновление записи модели Enterprise в БД.
    """
    return await create_or_update_with_session_get(
        session,
        'Enterprise',
        enterprise_data.dict(exclude_unset=True),
    )


@router.delete('/{id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_enterprise_ep(_id: PathIdDep, session: SessionDep):
    """
    Эндпоинт удаления Enterprise.
    """
    await delete_via_sql_delete(session, 'Enterprise', column('id') == _id)


@router.get('/')
async def get_enterprises_ep(session: SessionDep,
                             params: PaginParamsDep,
                             ids: GetParamsIdsDep,
                             ) -> LimitOffsetPage[EnterpriseOutSerializer]:
    """
    Отдает 1 или несколько записей Enterprise с пагинацией.
    """
    # return await get_enterprises(session, ids, params)
    return await get_collection_paginated(session, 'Enterprise', ids, params)
