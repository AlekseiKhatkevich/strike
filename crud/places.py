from typing import TYPE_CHECKING

from geoalchemy2 import functions as ga_functions
from sqlalchemy import exc as sa_exc
from sqlalchemy import select

from internal.constants import PLACES_DUPLICATION_RADIUS
from models import Place

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from serializers.places import PlaceInSerializer

__all__ = (
    'create_place',
)


async def create_place(session: 'AsyncSession', place_data: 'PlaceInSerializer') -> Place:
    """
    Создает инстанс модели Place и сохраняет его в БД.
    """
    try:
        async with session.begin_nested():
            session.add(instance := Place(**place_data.dict()))
    except sa_exc.IntegrityError as err:
        if 'close_points_exc_constraint' in err.args[0]:
            # noinspection PyTypeChecker,PyUnresolvedReferences
            known_places = await session.scalars(
                select(Place.name).where(
                    ga_functions.ST_Distance(Place.coordinates, place_data.coordinates) <= PLACES_DUPLICATION_RADIUS
                )
            )
            raise ValueError(
                f'Place {place_data.name} has one or few places within {PLACES_DUPLICATION_RADIUS} meters distance'
                f' {known_places.all()}. Can not be saved in database as it is a duplicate.'
            )
        else:
            raise err
    else:
        await session.commit()
        return instance
