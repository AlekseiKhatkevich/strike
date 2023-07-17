import pytest
from geoalchemy2 import WKTElement, WKBElement
from shapely import Point

from internal.database import Base
from internal.geo import point_from_wkt_or_wkb
from models import User


@pytest.mark.parametrize(
    'name, model',
    [
        ('User', User),
        pytest.param('HuiUser', None, marks=pytest.mark.xfail(
            raises=LookupError,
            strict=True,
        ))
    ]
)
def test_get_model_by_name(name, model):
    """
    Метод должен вернуть модель по ее имени или возбудить исключение если
    модель не была найдена.
    """
    assert Base.get_model_by_name(name) == model


def test_point_from_wkt_or_wkb_positive():
    """
    Позитивный тест ф-ции point_from_wkt_or_wkb.
    """
    point = Point(0, 0)
    wkt_point = WKTElement(data=point.wkt, srid=4326)
    wkb_point = WKBElement(data=point.wkb, srid=4326)

    assert point_from_wkt_or_wkb(wkt_point) == point
    assert point_from_wkt_or_wkb(wkb_point) == point
