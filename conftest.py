import asyncio
import datetime
from asyncio import AbstractEventLoop
from typing import Any, AsyncGenerator, Awaitable, Callable, TYPE_CHECKING

import pytest
import redis
from _pytest.logging import LogCaptureFixture
from fastapi import Request
from fastapi.testclient import TestClient
from httpx import AsyncClient
from loguru import logger
from sqlalchemy import text
from sqlalchemy.event import listens_for
from sqlalchemy.ext.asyncio import AsyncSession

from events import register_all_sqlalchemy_events
from internal.database import Base, async_session, engine
from internal.dependencies import get_session
from internal.redis import RedisConnectionContextManager, redis_connection
from main import app
from security.jwt import generate_jwt_token

if TYPE_CHECKING:
    from factory import Factory


pytest_plugins = [
    'tests.users.fixtures',
    'tests.plugins',
    'tests.region.fixtures',
    'tests.union.fixtures',
    'tests.enterprise.fixtures',
    'tests.place.fixtures',
    'tests.strike.fixtures',
    'tests.detentions.fixtures',
]


@pytest.fixture
def now() -> datetime.datetime:
    """
    Текущее время в utc.
    """
    return datetime.datetime.now(tz=datetime.UTC)


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
async def async_client_httpx(user_in_db) -> AsyncClient:
    """
    Ассинхронный клиент для тестирования апи.
    """
    async with AsyncClient(
            app=app,
            base_url='http://localhost:8000/',
            headers={'Authorization': f'Bearer {generate_jwt_token(user_in_db.id)}'}
    ) as client:
        yield client


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Сессия которая не коммитит в БД. Нужна для тестирования.
    https://github.com/sqlalchemy/sqlalchemy/issues/5811#issuecomment-755871691
    """
    async with engine.connect() as conn:
        await conn.begin()

        await conn.begin_nested()

        async with async_session(bind=conn) as session:

            @listens_for(session.sync_session, 'after_transaction_end')
            def end_savepoint(*args, **kwargs):
                if conn.closed:
                    return

                if not conn.in_nested_transaction():
                    conn.sync_connection.begin_nested()

            yield session


@pytest.fixture(autouse=True)
def override_session_for_tests(db_session) -> None:
    """
    Замена обычной сессии БД на сессию полностью транзакционную.
    https://www.fastapitutorial.com/blog/unit-testing-in-fastapi/
    """

    def _get_test_db():
        yield db_session

    app.dependency_overrides[get_session] = _get_test_db


@pytest.fixture(scope='session', autouse=True)
async def truncate_db(request):
    """
    Чистим базу после каждой сессии на всякий случай.
    """
    if 'no_db_calls' not in request.keywords:
        tables = [table.name for table in Base.metadata.sorted_tables]
        statement = text("TRUNCATE {} RESTART IDENTITY CASCADE;".format(', '.join(tables)))
        async with async_session() as session:
            await session.execute(statement)
            await session.commit()

    yield None


@pytest.fixture(autouse=True)
async def clean_redis_after_each_test() -> None:
    """
    Подчищаем редис после каждого теста.
    """
    yield None
    try:
        await redis_connection.flushdb()
    finally:
        await redis_connection.close()


@pytest.fixture(scope='session')
def event_loop() -> AbstractEventLoop:
    """
    Заменяем стандартную фикстуру event_loop так как с ней есть проблемы.
    https://stackoverflow.com/questions/61022713/pytest-asyncio-has-a-closed-event-loop-but-only-when-running-all-tests
    """
    try:
        loop = asyncio.get_running_loop()
        yield loop
    except RuntimeError:
        loop = asyncio.new_event_loop()
        yield loop
    finally:
        loop.close()


@pytest.fixture
async def redis_conn() -> redis.Redis:
    """
    Коннект к редису.
    """
    async with RedisConnectionContextManager(redis_connection) as conn:
        yield conn


@pytest.fixture(scope='session', autouse=True)
def register_sqlalchemy_events():
    """
    Регистрируем эвенты sqlalchemy
    """
    register_all_sqlalchemy_events()


@pytest.fixture
async def create_instance_from_factory(db_session: 'AsyncSession') -> Callable[['Factory', Any, ...], Awaitable['Base']]:
    """
    Создает инстанс модели из полученной фабрики и сохраняет его в БД.
    """
    async def _inner(_factory, *args, **kwargs):
        instance = _factory.build(*args, **kwargs)
        db_session.add(instance)
        await db_session.commit()
        return instance
    return _inner


@pytest.fixture(scope='session', autouse=True)
def faker_session_locale():
    """
    https://faker.readthedocs.io/en/master/pytest-fixtures.html
    """
    return ['ru_RU']


@pytest.fixture
def fake_request() -> Request:
    """
    Типа реквест.
    """
    return Request(scope={'type': 'http'})
