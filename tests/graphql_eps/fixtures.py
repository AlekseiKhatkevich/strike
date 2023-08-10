import functools
from typing import Callable, TYPE_CHECKING

import pytest

from graphql_related.main import schema

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def schema_f(db_session: 'AsyncSession') -> Callable:
    """
    "schema.execute" для тестов GraphQL с добавленной в контекст сессией.
    """
    return functools.partial(schema.execute, context_value={'session': db_session})
