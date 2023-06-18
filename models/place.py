from geoalchemy2 import Geography
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from internal.constants import RU_RU_CE_COLLATION_NAME
from internal.database import Base
from internal.typing_and_types import BigIntType
from models.annotations import BigIntPk

__all__ = (
    'Place',
)


class Place(Base):
    """

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
    coordinates: Mapped[tuple[float, float] | None] = mapped_column(
        Geography(geometry_type='POINT', spatial_index=True),
    )

    def __repr__(self):
        return f'Place "{self.name}" in region {self.region_name}.'

    __table_args__ = (
        UniqueConstraint(name, region_name,),
    )
# p.coordinates = WKTElement('POINT(5.33 45.44)')
# a = await  session.scalar(select(functions.ST_AsText(Place.coordinates)).where(Place.id==1))
