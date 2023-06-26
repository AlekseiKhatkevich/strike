from decimal import Decimal

import pytest
from geoalchemy2 import WKTElement

from serializers.places import PlaceInSerializer, PlaceOutSerializer


@pytest.mark.parametrize('coords,_type', [((22.0, 33.0), WKTElement), (None, type(None))])
def test_PlaceInSerializer_positive(place_factory, coords, _type):
    """
    Позитивный тест сериалайзера PlaceInSerializer используемого для создания новой
    записи модели Place.
    """
    place = place_factory.build()
    input_data = dict(
        name=place.name,
        address=place.address,
        region_name=place.region.name,
    )
    if coords is not None:
        input_data['coordinates'] = coords

    serializer = PlaceInSerializer(
       **input_data
    )
    assert isinstance(serializer.coordinates, _type)


def test_PlaceOutSerializer_positive(place_factory):
    """
    Позитивный тест сериалайзера PlaceOutSerializer используемого для отдачи на фронт в респонсе
    новой записи модели Place.
    """
    orig_coords = (22.0, 33.3)
    place = place_factory.build(coords_in_decimal=orig_coords)

    serializer = PlaceOutSerializer(
        name=place.name,
        address=place.address,
        region_name=place.region.name,
        coordinates=place.coordinates,
        id=1,
    )

    assert all(isinstance(c, Decimal) for c in serializer.coordinates)
    assert serializer.coordinates == orig_coords
