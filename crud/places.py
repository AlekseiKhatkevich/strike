from typing import TYPE_CHECKING

from geoalchemy2 import functions as ga_functions
from sqlalchemy import exc as sa_exc
from sqlalchemy import select

from internal.constants import PLACES_DUPLICATION_RADIUS

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from models import Place


__all__ = (
    'create_place',
)


async def create_place(session: 'AsyncSession', place: 'Place') -> 'Place':
    """
    Создает инстанс модели Place и сохраняет его в БД.
    """
    place_model = type(place)
    try:
        async with session.begin_nested():
            session.add(place)
    except sa_exc.IntegrityError as err:
        if 'close_points_exc_constraint' in err.args[0]:
            # noinspection PyTypeChecker,PyUnresolvedReferences
            known_places = await session.scalars(
                select(place_model.name).where(
                    ga_functions.ST_Distance(place_model.coordinates, place.coordinates) <= PLACES_DUPLICATION_RADIUS
                )
            )
            raise ValueError(
                f'Place {place.name} has one or few places within {PLACES_DUPLICATION_RADIUS} meters distance'
                f' {known_places.all()}. Can not be saved in database as it is a duplicate.'
            )
        else:
            raise err
    else:
        await session.commit()
        return place
