from fastapi import APIRouter, Depends, Query

from crud.unions import get_unions
from internal.dependencies import SessionDep, jwt_authorize
from serializers.unions import UnionOutSerializer

__all__ = (
    'router',
)


router = APIRouter(tags=['union'], dependencies=[Depends(jwt_authorize)])


@router.get('/')
async def unions(session: SessionDep,
                 id: list[int] = Query([], ge=1),
                 ) -> list[UnionOutSerializer]:
    """
    Отдача записей Union.
    """
    unions = await get_unions(session, id)
    return unions.all()
    # пагиниция

