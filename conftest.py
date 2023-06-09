import asyncio
from typing import AsyncGenerator

import pytest
from _pytest.logging import LogCaptureFixture
from fastapi.testclient import TestClient
from httpx import AsyncClient
from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from internal.database import Base, async_session
from internal.dependencies import get_session, get_db_session_test
from main import app

pytest_plugins = [
    'tests.users.fixtures',
]


@pytest.fixture
def caplog(caplog: LogCaptureFixture):
    """
    https://loguru.readthedocs.io/en/stable/resources/migration.html#replacing-caplog-fixture-from-pytest-library
    """
    handler_id = logger.add(
        caplog.handler,
        format="{message}",
        level=0,
        filter=lambda record: record["level"].no >= caplog.handler.level,
        enqueue=False,  # Set to 'True' if your test is spawning child processes.
    )
    yield caplog
    logger.remove(handler_id)


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


db_session: AsyncGenerator[AsyncSession, None] = pytest.fixture(get_session)
"""
Фикстура сессии БД
"""


# @pytest.fixture(scope='session', autouse=True)
# def override_session_for_tests() -> None:
#     """
#     Замена обычной сессии БД на сессию полностью транзакционную.
#     """
#     app.dependency_overrides[get_session] = get_db_session_test


@pytest.fixture(scope='function', autouse=True)
async def truncate_db(request):
    """
    Чистим базу после каждой сессии на всякий случай.
    """
    yield None

    # async def _trunc():
    #     tables = [table.name for table in Base.metadata.sorted_tables]
    #     statement = text("TRUNCATE {} RESTART IDENTITY CASCADE;".format(', '.join(tables)))
    #     async with async_session() as session:
    #         await session.execute(statement)
    #         await session.commit()
    #
    # asyncio.run(_trunc())
    if 'no_db_calls' not in request.keywords:
        tables = [table.name for table in Base.metadata.sorted_tables]
        statement = text("TRUNCATE {} RESTART IDENTITY CASCADE;".format(', '.join(tables)))
        async with async_session() as session:
            await session.execute(statement)
            await session.commit()
