from decimal import Decimal

from geoalchemy2 import Geography, WKTElement, WKBElement, Geometry
from geoalchemy2 import functions as ga_functions
from geoalchemy2.functions import ST_Buffer
from sqlalchemy import String, ForeignKey, UniqueConstraint, CheckConstraint, func
from sqlalchemy.dialects.postgresql import ExcludeConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.expression import cast

from internal.constants import RU_RU_CE_COLLATION_NAME, PLACES_DUPLICATION_RADIUS
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
        ForeignKey('regions.name', ondelete='RESTRICT', onupdate='CASCADE', ),
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
    region: Mapped['Region'] = relationship()

    def __repr__(self):
        return f'Place "{self.name}" in region {self.region_name}.'

    __table_args__ = (
        CheckConstraint(
            (func.abs(ga_functions.ST_X(cast(coordinates, Geometry))) <= 180) &
            (func.abs(ga_functions.ST_Y(cast(coordinates, Geometry))) <= 90),
            name='coordinates_limit',
        ),
        UniqueConstraint(name, region_name, ),
        #  https://stackoverflow.com/questions/76500152/postgres-create-unique-index-on-point-within-certain-distance-around-it/76500390?noredirect=1#comment134891135_76500390
        ExcludeConstraint(
            (ST_Buffer(coordinates, PLACES_DUPLICATION_RADIUS, 'quad_segs=1'), '&&'),
            name='close_points_exc_constraint',
        ),
    )

    @hybrid_property
    def coords_hr(self) -> tuple[Decimal, Decimal] | None:
        """
        Возвращает координаты в числовом формате широта, долгота.
        """
        if isinstance(self.coordinates, WKTElement):
            import shapely.wkt as loader
        elif isinstance(self.coordinates, WKBElement):
            import shapely.wkb as loader
        else:
            return self.coordinates
        sh_point = loader.loads(self.coordinates.data)
        return Decimal(sh_point.y), Decimal(sh_point.x)

    # noinspection PyNestedDecorators
    @coords_hr.inplace.expression
    @classmethod
    def _coords_hr_expression(cls) -> str:
        # noinspection PyUnresolvedReferences
        return ga_functions.ST_AsLatLonText(ga_functions.ST_AsText(cls.coordinates), 'D°M''S.SSS"C')
