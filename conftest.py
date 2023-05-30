import asyncio

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.event import listens_for

from database import engine, Base, async_session
from main import app


#  фикстура eventloop встроена и доступна через pytest-asyncio

@pytest.fixture(scope='module')
def client():
    return TestClient(app)


@pytest.fixture
async def async_client_httpx():
    async with AsyncClient(app=app) as client:
        yield client


@pytest.fixture
async def db_session_with_truncate():

    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

        tables = [table.name for table in Base.metadata.sorted_tables]
        statement = text("TRUNCATE {} RESTART IDENTITY CASCADE;".format(', '.join(tables)))
        await conn.execute(statement)
        await conn.commit()

    async with async_session() as _session:
        yield _session


@pytest.fixture
async def recreate_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all(engine))
        await conn.run_sync(Base.metadata.create_all(engine))


@pytest.fixture
async def db_session_old_version():
    """
    https://stackoverflow.com/questions/67255653/how-to-set-up-and-tear-down-a-database-between-tests-in-fastapi
    """
    async with engine.connect() as connection:
        transaction = connection.begin()
        async with async_session(bind=connection) as session:

            # Begin a nested transaction (using SAVEPOINT).
            nested = await connection.begin_nested()

            # If the application code calls session.commit, it will end the nested
            # transaction. Need to start a new one when that happens.
            @listens_for(session.sync_session, 'after_transaction_end')
            async def end_savepoint(session, transaction):
                nonlocal nested
                if not nested.is_active:
                    nested = await connection.begin_nested()

            yield session

        # Rollback the overall transaction, restoring the state before the test ran.
        transaction.rollback()


@pytest.fixture
async def db_session():
    """
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


@pytest.fixture(scope='session', autouse=True)
def setup_database():
    async def _action():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(_action())


# register(UserInFactory)

