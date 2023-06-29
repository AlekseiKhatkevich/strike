from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    status,
    HTTPException,
    Path,
)

from crud.places import create_or_update_place, delete_place, calculate_distance
from internal.dependencies import jwt_authorize, SessionDep
from models import Place
from serializers.places import (
    PlaceInSerializer,
    PlaceOutSerializer,
    PlaceDeleteSerializer,
)

__all__ = (
    'router',
)


router = APIRouter(tags=['places'], dependencies=[Depends(jwt_authorize)])


@router.get('/distance/{id1}/{id2}/')
async def distance_between_2_points(id1: Annotated[int, Path(title='first Place id', ge=1)],
                                    id2: Annotated[int, Path(title='second Place id', ge=1)],
                                    session: SessionDep,
                                    ) -> float | None:
    """
    Дистанция м/у 2-мя точками по геоиду.
    """
    return await calculate_distance(session, id1, id2)


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
    Удаление записи Place.
    """
    await delete_place(session, place_data.lookup_kwargs)
