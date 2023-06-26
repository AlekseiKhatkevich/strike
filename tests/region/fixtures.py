from typing import TYPE_CHECKING

import pytest
from pytest_factoryboy import register

from tests.factories.region import RegionFactory

if TYPE_CHECKING:
    from models import Region

register(RegionFactory)


@pytest.fixture
async def region(region_factory: RegionFactory, create_instance_from_factory) -> 'Region':
    """
    Создает запись модели Region в БД.
    """
    return await create_instance_from_factory(region_factory)
