import asyncio
from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import text

from internal.database import Base, async_session
from internal.dependencies import get_session, get_db_session_test
from main import app

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def client() -> TestClient:
    """
    Клиент для тестирования API.
    """
    return TestClient(app)


@pytest.fixture
async def async_client_httpx() -> AsyncClient:
    """
    Ассинхронный клиент для тестирования апи.
    """
    async with AsyncClient(app=app, base_url='http://localhost:8000/') as client:
        yield client


db_session: 'AsyncSession' = pytest.fixture(get_db_session_test)
"""
Фикстура сессии БД
"""


@pytest.fixture(scope='session', autouse=True)
def override_session_for_tests() -> None:
    """
    Замена обычной сессии БД на сессию полностью транзакционную.
    """
    app.dependency_overrides[get_session] = get_db_session_test


@pytest.fixture(scope='session', autouse=True)
def truncate_db():
    """
    Чистим базу после каждой сессии на всякий случай.
    """
    yield None

    async def _trunc():
        tables = [table.name for table in Base.metadata.sorted_tables]
        statement = text("TRUNCATE {} RESTART IDENTITY CASCADE;".format(', '.join(tables)))
        async with async_session() as session:
            await session.execute(statement)
            await session.commit()

    asyncio.run(_trunc())
