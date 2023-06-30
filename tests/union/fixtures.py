from typing import TYPE_CHECKING

import pytest
from pytest_factoryboy import register

from tests.factories.union import UnionFactory

if TYPE_CHECKING:
    from models import Union

register(UnionFactory)


@pytest.fixture
async def union(union_factory, create_instance_from_factory) -> 'Union':
    """
     Создает и сохраняет в БД экз. кл. Union (профсоюз).
    """
    return await create_instance_from_factory(union_factory)


@pytest.fixture
async def unions_batch(db_session, union_factory) -> list['Union']:
    """
    10 записей Union в БД.
    """
    unions = union_factory.build_batch(10)
    db_session.add_all(unions)
    await db_session.commit()
    return unions

