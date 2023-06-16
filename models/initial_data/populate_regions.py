from loguru import logger
from sqlalchemy.dialects.postgresql import insert

from internal.database import async_session
from models import Region
from models.initial_data import RU_regions

__all__ = (
    'populate',
)


async def populate() -> None:
    """
    Пишет все регионы РФии в табличку.
    """
    async with async_session() as session:
        data = [{'name': reg_name} for reg_name in RU_regions.names]
        await session.execute(
            insert(Region).on_conflict_do_nothing(),
            data,
        )
        await session.commit()
        logger.info(
            f'Regions are successfully saved into "{Region.__tablename__}" table.'
        )
