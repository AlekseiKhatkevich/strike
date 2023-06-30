from typing import TYPE_CHECKING
from shapely import Point
import pytest
from pytest_factoryboy import register

from tests.factories.region import RegionFactory

if TYPE_CHECKING:
    from models import Region

register(RegionFactory)


@pytest.fixture
async def region(region_factory: RegionFactory, db_session) -> 'Region':
    """
    Создает запись модели Region в БД.
    """
    instance = region_factory(point=Point(21, 31)).build()
    db_session.add(instance)
    await db_session.commit()
    return instance
