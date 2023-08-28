import datetime
from dataclasses import dataclass
from typing import Iterable
from loguru import logger
from shapely import LineString
from sqlalchemy.dialects.postgresql import Range

from models import KafkaRoute
from serializers.for_kafka import KafkaCoordinatesDeSerializer

__all__ = (
    'save_route_into_db',
    'CoorsPreparer',
)


@dataclass
class CoorsPreparer:
    user_id: int
    coords: Iterable[KafkaCoordinatesDeSerializer]

    @property
    def data_for_saving(self):
        tmin = min(c.timestamp for c in self.coords) / 1000
        tmax = max(c.timestamp for c in self.coords) / 1000
        tmin_dt = datetime.datetime.fromtimestamp(tmin).astimezone(datetime.UTC)
        tmax_dt = datetime.datetime.fromtimestamp(tmax).astimezone(datetime.UTC)
        duration = Range(tmin_dt, tmax_dt)
        linestring = LineString(c.point for c in self.coords)

        return dict(
            duration=duration,
            user_id=self.user_id,
            linesating=linestring,
        )


async def save_route_into_db(session, data):
    instance = KafkaRoute(**data)
    session.add(instance)
    instance = await session.commit()
    logger.info(f'Route {instance} has been just saved into DB.')
