from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi_pagination import LimitOffsetPage

from crud.helpers import create_or_update_with_session_get, delete_via_sql_delete
from crud.unions import get_unions
from internal.dependencies import PaginParamsDep, PathIdDep, SessionDep, jwt_authorize
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
    try:
        return await create_or_update_with_session_get(session, 'Union', union_data.dict(exclude_none=True))
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Union with id={union_data.id} is not exists.'
        ) from err


@router.delete('/{id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_union_ep(id: PathIdDep, session: SessionDep):
    """
    Эндпоинт удаления Union.
    """
    await delete_via_sql_delete(session, 'Union', id=id)
