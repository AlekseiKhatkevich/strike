from fastapi import APIRouter, Depends, Query, status
from fastapi import APIRouter, Depends, Query, status
from fastapi_pagination import LimitOffsetPage

from crud.helpers import create_or_update_with_session_get, delete_via_sql_delete
from crud.unions import get_unions
from internal.dependencies import PaginParamsDep, PathIdDep, SessionDep, jwt_authorize
from internal.model_logging import create_log
from models import Union
from serializers.unions import UnionInSerializer, UnionOutSerializer

__all__ = (
    'router',
)

router = APIRouter(tags=['union'], dependencies=[Depends(jwt_authorize)])


@router.get('/')
async def unions(session: SessionDep,
                 params: PaginParamsDep,
                 _id: list[int] = Query([], alias='id'),
                 ) -> LimitOffsetPage[UnionOutSerializer]:
    """
    Отдача записей Union с пагинацией.
    """
    collection = await get_unions(session, _id, params)
    out = LimitOffsetPage[UnionOutSerializer]

    return out.create(collection.items, params, total=collection.total)


@router.post('/', status_code=status.HTTP_201_CREATED)
@router.put('/')
@create_log
async def create_or_update_union_ep(session: SessionDep,
                                    union_data: UnionInSerializer,
                                    ) -> UnionOutSerializer:
    """
    Создание или изменение записей Union.
    """
    return await create_or_update_with_session_get(session, 'Union', union_data.model_dump(exclude_none=True))


@router.delete('/{id}/', status_code=status.HTTP_204_NO_CONTENT)
@create_log
async def delete_union_ep(session: SessionDep, id: PathIdDep):
    """
    Эндпоинт удаления Union.
    """
    return await delete_via_sql_delete(session, Union, Union.id == id)
