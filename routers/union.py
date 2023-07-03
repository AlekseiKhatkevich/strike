from fastapi import APIRouter, Depends, Query, status
from fastapi_pagination import LimitOffsetPage

from crud.helpers import create_or_update_with_session_get
from crud.unions import get_unions
from internal.dependencies import PaginParamsDep, SessionDep, jwt_authorize
from serializers.unions import UnionInSerializer, UnionOutSerializer

__all__ = (
    'router',
)

router = APIRouter(tags=['union'], dependencies=[Depends(jwt_authorize)])


@router.get('/')
async def unions(session: SessionDep,
                 params: PaginParamsDep,
                 id: list[int] = Query([], ge=1),
                 ) -> LimitOffsetPage[UnionOutSerializer]:
    """
    Отдача записей Union с пагинацией.
    """
    return await get_unions(session, id, params)


@router.post('/', status_code=status.HTTP_201_CREATED)
@router.put('/')
async def create_or_update_union_ep(session: SessionDep,
                                    union_data: UnionInSerializer,
                                    ) -> UnionOutSerializer:
    """
    Создание или изменение записей Union.
    """
    return await create_or_update_with_session_get(session, 'Union', union_data.dict())
