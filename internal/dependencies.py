from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings, Settings
from .database import async_session

__all__ = (
    'SessionDep',
    'SettingsDep',
    'get_session',
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Асинхронная сессия БД.
    """
    async with async_session() as _session:
        yield _session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
