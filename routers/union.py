from fastapi import APIRouter, Depends, Query
from fastapi_pagination import LimitOffsetPage

from crud.unions import get_unions
from internal.dependencies import PaginParamsDep, SessionDep, jwt_authorize
from serializers.unions import UnionOutSerializer

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
