from numbers import Number

from geoalchemy2 import WKTElement

__all__ = (
    'point_from_numeric',
)


def point_from_numeric(lat: Number, lon: Number, srid: int = 4326) -> WKTElement:
    """
    Geo элемент POINT для сохранения в БД из широты и долготы во флоате или чем то подобном.
    """
    assert -90 <= lat <= 90 and -180 <= lon <= 180, 'This is geo coordinates for christ sake!!!'
    return WKTElement(f'POINT({lon} {lat})', srid=srid)
    # сначала долгота потом только широта! долгота - Х, широта - У
