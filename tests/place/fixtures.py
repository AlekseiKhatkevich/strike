import pytest
from pytest_factoryboy import register

from tests.factories.place import PlaceFactory

register(PlaceFactory)


@pytest.fixture
async def place(db_session, place_factory):
    """
    Инстанс модели Place сохраненный в БД.
    """
    instance = place_factory.build()
    db_session.add(instance)
    await db_session.commit()
    return instance
