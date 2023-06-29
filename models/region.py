from geoalchemy2 import Geography
from sqlalchemy.orm import Mapped, mapped_column

from internal.database import Base

__all__ = (
    'Region',
)


class Region(Base):
    """
    Регион РФ.
    """
    __tablename__ = 'regions'

    name: Mapped[str] = mapped_column(
        primary_key=True,
    )
    contour = mapped_column(
        Geography(geometry_type='MultiPolygon', spatial_index=True),
        nullable=False,
        deferred=True,
    )

    def __repr__(self):
        return f'Region {self.name}'



# q = select(Region).select_from(Region)
# q = q.select_from(join(Place, Region, func.ST_Intersects(Region.contour, Place.coordinates)))
# res = await session.scalar(q.where(Place.id == 17))

