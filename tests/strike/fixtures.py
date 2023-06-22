from typing import TYPE_CHECKING, Awaitable, Callable, Any

import pytest
from pytest_factoryboy import register

from tests.factories.strike import StrikeFactory, StrikeToUserAssociationFactory

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from models import Strike

register(StrikeFactory)
register(StrikeToUserAssociationFactory)


@pytest.fixture
async def strike(db_session: 'AsyncSession',
                 strike_factory: StrikeFactory,
                 create_instance_from_factory: Callable[['AsyncSession', 'Factory', Any, ...], Awaitable['Strike']],
                 ) -> Awaitable['Strike']:
    """
    Инстанс модели Strike сохраненный в БД.
    """
    return await create_instance_from_factory(db_session, strike_factory)


@pytest.fixture()
async def strike_p(db_session: 'AsyncSession',
                   strike_factory: StrikeFactory,
                   create_instance_from_factory,
                   ) -> Callable[[Any, Any], Awaitable['Strike']]:
    """
    `strike` с возможностью передачи доп аргументов.
    """
    async def _inner(*args, **kwargs):
        return await create_instance_from_factory(db_session, strike_factory, *args, **kwargs)
    return _inner
