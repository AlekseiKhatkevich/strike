from typing import Any, Awaitable, Callable, TYPE_CHECKING

from pytest_factoryboy import register
import pytest

from tests.factories.detention import DetentionFactory, JailFactory

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from factory import Factory
    from models import Detention, Jail

register(JailFactory)
register(DetentionFactory)


@pytest.fixture
async def jail(jail_factory: JailFactory,
               create_instance_from_factory: Callable[['AsyncSession', 'Factory', Any, ...], Awaitable['Jail']],
               ) -> Awaitable['Jail']:
    """
    Инстанс модели Jail сохраненный в БД.
    """
    return await create_instance_from_factory(jail_factory)


@pytest.fixture
async def detention(detention_factory: DetentionFactory,
                    create_instance_from_factory: Callable[
                        ['AsyncSession', 'Factory', Any, ...], Awaitable['Detention']],
                    ) -> Awaitable['Detention']:
    """
    Инстанс модели Detention сохраненный в БД.
    """
    return await create_instance_from_factory(detention_factory)
