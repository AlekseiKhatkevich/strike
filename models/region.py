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
    )

    def __repr__(self):
        return f'Region {self.name}'
