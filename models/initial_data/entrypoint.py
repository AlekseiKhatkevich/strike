import asyncio
import contextlib
import inspect
import sys
import logging

from . import *
# Не удалять импорт from . *  !!!

# python3 -m  models.initial_data.entrypoint  запускать так

logger = logging.getLogger(__name__)


def pred(obj) -> bool:
    """
    Имеет ли объект атрибут 'populate'
    """
    with contextlib.suppress(AttributeError):
        return bool(obj.populate)


async def main() -> None:
    """
    Запускает все задачи по загрузке данных в БД асинхронно.
    """
    awaitables = [obj.populate() for _, obj in inspect.getmembers(sys.modules[__name__], pred)]
    logger.info(f'Found {len(awaitables)} tasks to run. Running them all asynchronously.')
    results = await asyncio.gather(*awaitables, return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            logger.exception(f'Got an exception {result}', exc_info=result)


if __name__ == '__main__':
    asyncio.run(main())
