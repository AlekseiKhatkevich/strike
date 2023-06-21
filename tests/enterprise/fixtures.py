from typing import TYPE_CHECKING

import pytest
from pytest_factoryboy import register

from tests.factories.enterprise import EnterpriseFactory

if TYPE_CHECKING:
    from models import Enterprise
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def enterprise_instance(db_session: 'AsyncSession', enterprise_factory: EnterpriseFactory) -> 'Enterprise':
    """
    Компания с созданным регионом.
    """
    instance = enterprise_factory.build()
    db_session.add(instance)
    await db_session.commit()
    return instance


register(EnterpriseFactory)
