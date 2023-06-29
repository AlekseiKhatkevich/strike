import contextlib
from decimal import Decimal
from functools import cached_property

from geoalchemy2 import (
    Geography,
    Geometry,
    WKBElement,
    WKTElement,
    functions as ga_func,
)
from pyproj import Geod
from shapely import LineString, Point
from sqlalchemy import (
    CheckConstraint,
    ColumnElement,
    DECIMAL,
    ForeignKey,
    String,
    UniqueConstraint,
    cast,
    func,
    select,
)
from sqlalchemy.dialects.postgresql import ARRAY, ExcludeConstraint, array
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from internal.constants import PLACES_DUPLICATION_RADIUS, RU_RU_CE_COLLATION_NAME
from internal.database import Base
from internal.typing_and_types import BigIntType
from models.annotations import BigIntPk

from loguru import logger


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
        unique=True,
    )
    address: Mapped['str'] = mapped_column(
        String(256, collation=RU_RU_CE_COLLATION_NAME),
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
    region: Mapped['Region'] = relationship(
        # https://docs.sqlalchemy.org/en/20/orm/join_conditions.html#custom-operators-based-on-sql-functions
        primaryjoin='func.ST_Intersects(foreign(Place.coordinates), Region.contour).as_comparison(1, 2)',
        viewonly=True,
    )

    def __repr__(self):
        return f'Place "{self.name}"'

    __table_args__ = (
        CheckConstraint(
            (func.abs(ga_func.ST_X(cast(coordinates, Geometry))) <= 180) &
            (func.abs(ga_func.ST_Y(cast(coordinates, Geometry))) <= 90),
            name='coordinates_limit',
        ),
        #  https://stackoverflow.com/questions/76500152/postgres-create-unique-index-on-point-within-certain-distance-around-it/76500390?noredirect=1#comment134891135_76500390
        ExcludeConstraint(
            (ga_func.ST_Buffer(coordinates, PLACES_DUPLICATION_RADIUS, 'quad_segs=1'), '&&'),
            name='close_points_exc_constraint',
        ),
    )

    @cached_property
    def shapely_point(self) -> Point | None:
        """
        Получение POINT Shapely.
        """
        if isinstance(self.coordinates, WKTElement):
            import shapely.wkt as loader
        elif isinstance(self.coordinates, WKBElement):
            import shapely.wkb as loader
        else:
            return self.coordinates
        return loader.loads(self.coordinates.data)

    @hybrid_property
    def coords_hr(self) -> tuple[Decimal, Decimal] | None:
        """
        Возвращает координаты в числовом формате широта, долгота.
        """
        sh_point = self.shapely_point
        with contextlib.suppress(AttributeError):
            return Decimal(sh_point.y), Decimal(sh_point.x)

    # noinspection PyNestedDecorators
    @coords_hr.inplace.expression
    @classmethod
    def _coords_hr_expression(cls) -> ColumnElement[str | None]:
        """
        Строковое представление координат.
        """
        # noinspection PyUnresolvedReferences
        return ga_func.ST_AsLatLonText(ga_func.ST_AsText(cls.coordinates), 'D°M''S.SSS"C')

    @hybrid_property
    def coords_in_decimal(self) -> tuple[Decimal, Decimal] | None:
        return self.coords_hr

    # noinspection PyNestedDecorators,PyTypeChecker,PyUnresolvedReferences
    @coords_in_decimal.inplace.expression
    @classmethod
    def _coords_in_decimal_expression(cls) -> ColumnElement[list[Decimal | None, Decimal | None]]:
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
    def distance(self, other: 'Place') -> float | None:
        """
        Расстояние м/у 2-мя точками в км.
        https://gis.stackexchange.com/questions/403637/convert-distance-in-shapely-to-kilometres
        """
        if None in {self.coordinates, other.coordinates}:
            logger.warning(
                f'Can not calculate distance as one of coord is None {self.coordinates, other.coordinates}. '
                f'First Place id - {self.id}, other Place id - {other.id}.'
            )
            return None
        geod = Geod(ellps='WGS84')
        line_string = LineString(
            [self.shapely_point, other.shapely_point]
        )
        return geod.geometry_length(line_string) / 1000

    # noinspection PyNestedDecorators,PyTypeChecker
    @distance.inplace.expression
    @classmethod
    def _distance_expression(cls, other_id) -> ColumnElement[float | None]:
        """
        Дистанция в км между собой и второй точкой.
        example select(Place.distance(86)).where(Place.id==85)
        """
        # noinspection PyUnresolvedReferences
        return ga_func.ST_Distance(
            Place.coordinates,
            select(Place.coordinates).where(Place.id == other_id).scalar_subquery(),
        ) / 1000
