from fastapi import (
    APIRouter,
    Depends,
    status,
)

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
    return place_data.coordinates