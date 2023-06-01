from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.event import listens_for
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings, Settings
from internal.database import async_session, engine

__all__ = (
    'SessionDep',
    'SettingsDep',
    'get_session',
)


async def get_db_session_test():
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


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Асинхронная сессия БД.
    """
    async with async_session() as _session:
        yield _session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
