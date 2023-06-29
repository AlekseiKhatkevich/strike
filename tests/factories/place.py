import factory
import pyproj
import json
from shapely.geometry import Point, mapping
from functools import partial
from shapely.ops import transform
from internal.geo import point_from_numeric
from models import Place

__all__ = (
    'PlaceFactory',
)


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
    buffer = point_transformed.buffer(250_000)

    buffer_wgs84 = transform(aeqd_to_wgs84, buffer)
    return buffer_wgs84


class PlaceFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Фабрика модели Place (место проведения забастовки).
    """
    name = factory.Faker('street_name', locale='ru_RU')
    address = factory.Faker('address', locale='ru_RU')
    coordinates = factory.LazyAttribute(
        lambda o: point_from_numeric(*o.coords_in_decimal)
    )
    region = factory.SubFactory('tests.factories.region.RegionFactory')

    class Meta:
        model = Place

    class Params:
        coords_in_decimal = factory.Faker('latlng')
