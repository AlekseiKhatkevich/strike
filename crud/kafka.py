import datetime
from dataclasses import dataclass
from typing import Any, Iterable, TYPE_CHECKING

from geoalchemy2 import WKTElement
from loguru import logger
from shapely import LineString
from sqlalchemy.dialects.postgresql import Range


from models import KafkaRoute
from serializers.for_kafka import KafkaCoordinatesDeSerializer

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = (
    'save_route_into_db',
    'CoorsPreparer',
)


@dataclass
class CoorsPreparer:
    """
    Подготовка набора координат к сохранению в качестве маршрута в БД.
    """
    user_id: int
    coords: Iterable[KafkaCoordinatesDeSerializer]

    @property
    def data_for_saving(self) -> dict[str, Any]:
        """
        Подготовленные данные для сохранения в БД.
        """
        tmin = min(c._timestamp for c in self.coords) / 1000
        tmax = max(c._timestamp for c in self.coords) / 1000
        tmin_dt = datetime.datetime.fromtimestamp(tmin).astimezone(datetime.UTC)
        tmax_dt = datetime.datetime.fromtimestamp(tmax).astimezone(datetime.UTC)
        duration = Range(tmin_dt, tmax_dt)
        linestring = WKTElement(LineString(c.point for c in self.coords).wkt, srid=4326)

        return dict(
            duration=duration,
            user_id=self.user_id,
            linestring=linestring,
            num_points=len(self.coords),
        )


async def save_route_into_db(session: 'AsyncSession', data: dict[str, Any]) -> KafkaRoute:
    """
    Сохранение маршрута в БД.
    """
    instance = KafkaRoute(**data)
    session.add(instance)
    await session.commit()
    logger.info(f'Route {instance} has been just saved into DB.')
    return instance
