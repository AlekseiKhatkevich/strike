from numbers import Number
from functools import singledispatch

from geoalchemy2 import WKBElement, WKTElement
from shapely import wkt, wkb

__all__ = (
    'point_from_numeric',
    'point_from_wkt_or_wkb',
)


def point_from_numeric(lat: Number, lon: Number, srid: int = 4326) -> WKTElement:
    """
    Geo элемент POINT для сохранения в БД из широты и долготы во флоате или чем то подобном.
    """
    assert -90 <= lat <= 90 and -180 <= lon <= 180, 'This is geo coordinates for christ sake!!!'
    return WKTElement(f'POINT({lon} {lat})', srid=srid)
    # сначала долгота потом только широта! долгота - Х, широта - У


@singledispatch
def point_from_wkt_or_wkb(coord_wkx_format):
    """
    Преобразует WKT или WKB полученные из БД в shapley POINT.
    """
    assert True, 'We are here and this is completely wrong'


@point_from_wkt_or_wkb.register
def _(coord_wkx_format: WKTElement):
    return wkt.loads(coord_wkx_format.data)


@point_from_wkt_or_wkb.register
def _(coord_wkx_format: WKBElement):
    return wkb.loads(coord_wkx_format.data)
