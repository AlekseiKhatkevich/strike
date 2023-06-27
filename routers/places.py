from fastapi import (
    APIRouter,
    Depends,
    status,
    HTTPException,
)

from crud.places import create_or_update_place, delete_place
from internal.dependencies import jwt_authorize, SessionDep
from models import Place
from serializers.places import PlaceInSerializer, PlaceOutSerializer, PlaceDeleteSerializer

__all__ = (
    'router',
)


router = APIRouter(tags=['places'], dependencies=[Depends(jwt_authorize)])


@router.post('/', status_code=status.HTTP_201_CREATED)
@router.put('/', status_code=status.HTTP_200_OK)
@router.patch('/', status_code=status.HTTP_200_OK)
async def create_or_update_place_ep(session: SessionDep, place_data: PlaceInSerializer) -> PlaceOutSerializer:
    """
    Создание новой записи модели Place (Место проведения забастовки) или обновление существующей.
    """
    try:
        instance = await create_or_update_place(session, Place(**place_data.dict()))
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err.args[0],
        )
    return instance


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_place_ep(session: SessionDep, place_data: PlaceDeleteSerializer):
    """
    """
    await delete_place(session, place_data.lookup_kwargs)
