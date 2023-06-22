from typing import TYPE_CHECKING

import pytest
from pytest_factoryboy import register

from tests.factories.strike import StrikeFactory, StrikeToUserAssociationFactory

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from models import Strike


register(StrikeFactory)
register(StrikeToUserAssociationFactory)


@pytest.fixture
async def strike(db_session: 'AsyncSession', strike_factory: StrikeFactory) -> 'Strike':
    """
    Инстанс модели Strike сохраненный в БД.
    """
    instance = strike_factory.build()
    db_session.add(instance)
    await db_session.commit()
    return instance
