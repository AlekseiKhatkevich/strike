from decimal import Decimal

from geoalchemy2 import Geography, WKTElement, WKBElement, Geometry
from geoalchemy2 import functions as ga_func
from geoalchemy2.functions import ST_Buffer
from pyproj import Geod
from shapely.geometry import LineString
from sqlalchemy import String, ForeignKey, UniqueConstraint, CheckConstraint, func, select
from sqlalchemy import cast, DECIMAL
from sqlalchemy.dialects.postgresql import ExcludeConstraint, ARRAY
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
            (func.abs(ga_func.ST_X(cast(coordinates, Geometry))) <= 180) &
            (func.abs(ga_func.ST_Y(cast(coordinates, Geometry))) <= 90),
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
        """
        Строковое представление координат.
        """
        # noinspection PyUnresolvedReferences
        return ga_func.ST_AsLatLonText(ga_func.ST_AsText(cls.coordinates), 'D°M''S.SSS"C')

    @hybrid_property
    def coords_in_decimal(self) -> tuple[Decimal, Decimal] | None:
        return self.coords_hr

    # noinspection PyNestedDecorators,PyTypeChecker
    @coords_in_decimal.inplace.expression
    @classmethod
    def _coords_in_decimal_expression(cls) -> list[Decimal, Decimal]:
        """
        Координаты в Decimal (широта, долгота).
        """
        return cast(
            array(
                (
                    ga_func.ST_Y(cast(cls.coordinates, Geometry)),
                    ga_func.ST_X(cast(cls.coordinates, Geometry))
                ),
            ), ARRAY(DECIMAL)
        )

    @hybrid_method
    def distance(self, other: 'Place') -> float:
        """
        Расстояние м/у 2-мя точками в км.
        https://gis.stackexchange.com/questions/403637/convert-distance-in-shapely-to-kilometres
        """
        geod = Geod(ellps='WGS84')
        line_string = LineString(
            [self.coords_in_decimal, other.coords_in_decimal]
        )
        return geod.geometry_length(line_string) / 1000

    # noinspection PyNestedDecorators
    @distance.inplace.expression
    @classmethod
    def _distance_expression(cls, other_id) -> float:
        """
        Дистанция в км между собой и второй точкой.
        example select(Place.distance(86)).where(Place.id==85)
        """
        return ga_func.ST_Distance(
            Place.coordinates,
            select(Place.coordinates).where(Place.id == other_id),
        )
