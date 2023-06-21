from geoalchemy2 import Geography
from geoalchemy2.functions import ST_Buffer
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from internal.constants import RU_RU_CE_COLLATION_NAME
from internal.database import Base
from internal.typing_and_types import BigIntType
from models.annotations import BigIntPk

__all__ = (
    'Place',
)


class Place(Base):
    """
    Место проведения забастовки.
    """
    __tablename__ = 'places'

    id: Mapped[BigIntPk]
    name: Mapped['str'] = mapped_column(
        String(128, collation=RU_RU_CE_COLLATION_NAME),
    )
    address: Mapped['str'] = mapped_column(
        String(256, collation=RU_RU_CE_COLLATION_NAME),
    )
    region_name: Mapped[BigIntType] = mapped_column(
        ForeignKey('regions.name', ondelete='RESTRICT', onupdate='CASCADE',),
    )
    coordinates = mapped_column(
        # https://github.com/geoalchemy/geoalchemy2/issues/137
        Geography(geometry_type='POINT', nullable=True, spatial_index=False),
    )

    strikes: Mapped[list['Strike']] = relationship(
        secondary='strike_to_place_associations',
        passive_deletes=True,
        back_populates='places',
    )

    def __repr__(self):
        return f'Place "{self.name}" in region {self.region_name}.'

    __table_args__ = (
        UniqueConstraint(name, region_name,),
        #  https://stackoverflow.com/questions/76500152/postgres-create-unique-index-on-point-within-certain-distance-around-it/76500390?noredirect=1#comment134891135_76500390
        ExcludeConstraint(
            (ST_Buffer(coordinates, 100, 'quad_segs=1'), '&&'),
            name='close_points_exc_constraint',
        ),
    )
# p.coordinates = WKTElement('POINT(5.33 45.44)')
# a = await  session.scalar(select(functions.ST_AsText(Place.coordinates)).where(Place.id==1))
# SELECT (ST_AsLatLonText(ST_AsText(coordinates), 'D°M''S.SSS"C')) from places
