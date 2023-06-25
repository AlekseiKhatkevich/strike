import csv
import sys
from pathlib import Path
from typing import Iterator

from loguru import logger
from sqlalchemy.dialects.postgresql import insert

from internal.database import async_session
from models import Region

__all__ = (
    'populate',
)

csv_file_path = Path('internal/data/admin_level_4.csv')


def _get_parsed_csv() -> Iterator[tuple[str, str]]:
    """
    Получает имя и мультиполигон региона из csv файла.
    """
    csv.field_size_limit(sys.maxsize)
    with csv_file_path.open(newline='') as file:
        reader = csv.reader(file, delimiter=';')
        next(reader, None)
        yield from ((row[1], row[0]) for row in reader)


async def populate() -> None:
    """
    Пишет все регионы РФии в табличку.
    """
    async with async_session() as session:
        data = [{'name': name, 'contour': contour} for name, contour in _get_parsed_csv()]
        await session.execute(
            insert(Region).on_conflict_do_nothing().inline(),
            data,
        )
        await session.commit()
        logger.info(
            f'Regions are successfully saved into "{Region.__tablename__}" table.'
        )
