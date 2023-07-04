from typing import TYPE_CHECKING
from shapely import Point
import pytest
from pytest_factoryboy import register

from tests.factories.region import RegionFactory

if TYPE_CHECKING:
    from models import Region

register(RegionFactory)


@pytest.fixture
async def region(db_session, region_factory: RegionFactory) -> 'Region':
    """
    Создает запись модели Region в БД.
    """
    instance = region_factory.build(point=Point(21, 31))
    db_session.add(instance)
    await db_session.commit()
    return instance
