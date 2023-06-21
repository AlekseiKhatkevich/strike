from numbers import Number

from geoalchemy2 import WKTElement

__all__ = (
    'point_from_numeric',
)


def point_from_numeric(lat: Number, lon: Number) -> WKTElement:
    """
    Geo элемент POINT для сохранения в БД из широты и долготы во флоате или чем то подобном.
    """
    return WKTElement(f'POINT({lat} {lon})')
