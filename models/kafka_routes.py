import datetime

from geoalchemy2 import Geography
from sqlalchemy import CheckConstraint, Column
from sqlalchemy.dialects.postgresql import ExcludeConstraint, Range, TSTZRANGE
from sqlalchemy.orm import Mapped, mapped_column

from internal.database import Base
from models.annotations import BigIntPk
from models.mixins import CreatedAtMixin

__all__ = (
    'KafkaRoute',
)


class KafkaRoute(CreatedAtMixin, Base):
    """
    Маршрут юзера переданный через кафку и собранный в linestring по набору координат
    маршрутных точек.
    """
    __tablename__ = 'kafka_routes'

    id: Mapped[BigIntPk]
    duration: Mapped[Range[datetime.datetime]] = mapped_column(
        TSTZRANGE(), index=True,
    )
    user_id: Mapped[int] = mapped_column()
    linestring = mapped_column(
        Geography(geometry_type='LINESTRING', nullable=False, spatial_index=True, srid=4326),
    )
    num_points: Mapped[int]

    def __repr__(self):
        return f'Route for user {self.user_id} during {self.duration}'

    __table_args__ = (
        CheckConstraint(user_id >= 1, name='user_id_gte_1'),
        ExcludeConstraint(
            (Column('duration'), '&&'),
            (Column('user_id'), '='),
            name='duration_user_id_exc_c',
        )
    )
