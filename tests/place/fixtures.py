import pytest
from pytest_factoryboy import register

from tests.factories.place import PlaceFactory

register(PlaceFactory)


@pytest.fixture
async def place(db_session, place_factory, region_factory):
    """
    Инстанс модели Place сохраненный в БД.
    """
    place_instance = place_factory.build()
    db_session.add(place_instance)
    region_instance = region_factory.build(point=place_instance.shapely_point)
    db_session.add(region_instance)

    await db_session.commit()
    return place_instance
