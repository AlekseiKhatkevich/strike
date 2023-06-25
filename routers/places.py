from fastapi import (
    APIRouter,
    Depends,
    status, HTTPException,
)

from crud.places import create_place
from internal.dependencies import jwt_authorize, SessionDep

__all__ = (
    'router',
)

from serializers.places import PlaceInSerializer

router = APIRouter(tags=['places'], dependencies=[Depends(jwt_authorize)])


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_new_place(session: SessionDep, place_data: PlaceInSerializer):
    """
    Создание новой записи модели Place (Место проведения забастовки).
    """
    try:
        instance = await create_place(session, place_data)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err.args[0],
        )
    return instance
