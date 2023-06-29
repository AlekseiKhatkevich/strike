from typing import TYPE_CHECKING

from geoalchemy2 import functions as ga_functions
from loguru import logger
from sqlalchemy import delete, exc as sa_exc, select

from crud.helpers import commit_if_not_in_transaction
from internal.constants import PLACES_DUPLICATION_RADIUS
from models import Place

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


__all__ = (
    'create_or_update_place',
    'delete_place',
    'calculate_distance',
)


@commit_if_not_in_transaction
async def calculate_distance(session: 'AsyncSession', id1: int, id2: int) -> float | None:
    """
    Отдает дистанцию по геоиду между двумя точками.
    """
    return await session.scalar(
        select(Place.distance(id2)).where(Place.id == id1)
    )


async def delete_place(session: 'AsyncSession', lookup_kwargs: dict[str, int | str]) -> bool:
    """
    Удаляет запись Place по id либо по name + region_name.
    """
    deleted_id = await session.scalar(
        delete(Place).filter_by(**lookup_kwargs).returning(Place.id)
    )
    await session.commit()
    if deleted_id is None:
        logger.error(f'No entries has been deleted. Lookup kwargs - {lookup_kwargs}')
    else:
        logger.info(f'Entry with id={deleted_id} was successfully deleted from DB.')
    return deleted_id is not None


async def create_or_update_place(session: 'AsyncSession', place: Place) -> Place:
    """
    Создает инстанс модели Place и сохраняет его в БД или обновляет уже существующую.
    Если place не имеет id -то сохраняем его в БД, а если имеет – то обновляем существующий по
    этому id инстанс и сохраняем его в БД.
    """
    action = 'create' if place.id is None else 'update'
    try:
        async with session.begin_nested():
            place_merged = await session.merge(place)
    except sa_exc.IntegrityError as err:
        if 'close_points_exc_constraint' in err.args[0]:
            # noinspection PyTypeChecker,PyUnresolvedReferences
            known_places = await session.scalars(
                select(Place.name).where(
                    ga_functions.ST_Distance(Place.coordinates, place.coordinates) <= PLACES_DUPLICATION_RADIUS
                )
            )
            err = ValueError(
                f'Place {place.name} has one or few places within {PLACES_DUPLICATION_RADIUS} meters distance'
                f' {known_places.all()}. Can not be saved in database as it is a duplicate.'
            )
            logger.exception(err)

        raise err
    else:
        await session.commit()
        logger.info(f'Place {place_merged} was successfully {action}d.')
        return place_merged
