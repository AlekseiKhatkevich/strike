from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import async_session

__all__ = (
    'SessionDep',
)


async def get_session() -> AsyncSession:
    """

    :return:
    """
    async with async_session() as _session:
        yield _session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
