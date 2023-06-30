from functools import partial

import factory
import pyproj
from geoalchemy2 import WKTElement
from shapely.geometry import Point
from shapely.geometry.multipolygon import MultiPolygon
from shapely.ops import transform

from models import Region
from models.initial_data import RU_regions

__all__ = (
    'RegionFactory',
)

RADIUS = 1


def _generate_polygon(point: Point):
    """
    https://gis.stackexchange.com/questions/268250/generating-polygon-representing-rough-100km-circle-around-latitude-longitude-poi
    """
    local_azimuthal_projection = \
        f"+proj=aeqd +R=6371000 +units=m +lat_0={point.y} +lon_0={point.x}"

    wgs84_to_aeqd = partial(
        pyproj.transform,
        pyproj.Proj('+proj=longlat +datum=WGS84 +no_defs'),
        pyproj.Proj(local_azimuthal_projection),
    )
    aeqd_to_wgs84 = partial(
        pyproj.transform,
        pyproj.Proj(local_azimuthal_projection),
        pyproj.Proj('+proj=longlat +datum=WGS84 +no_defs'),
    )
    point_transformed = transform(wgs84_to_aeqd, point)

    buffer = point_transformed.buffer(RADIUS)

    buffer_wgs84 = transform(aeqd_to_wgs84, buffer)
    return buffer_wgs84


class RegionFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Фабрика модели Region (регион РФ).
    """
    name = factory.Iterator(RU_regions.names)
    contour = factory.LazyAttribute(
        lambda o: WKTElement(
            MultiPolygon([_generate_polygon(o.point)]).wkt,
            srid=4326,
        ))

    class Meta:
        model = Region

    class Params:
        point = Point(11, 12)
