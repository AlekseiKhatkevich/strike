from database import async_session

__all__ = (
    'get_session',
)


async def get_session():
    async with async_session() as _session:
        yield _session
