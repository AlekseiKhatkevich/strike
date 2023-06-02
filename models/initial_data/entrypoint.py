import asyncio
import contextlib
import inspect
import sys

from . import populate_common_passwords
# не удалять импорт from . import populate_common_passwords  !!!

# python3 -m  models.initial_data.entrypoint  запускать так


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
    print(f'Found {len(awaitables)} tasks to run. Running them all asynchronously.')
    results = await asyncio.gather(*awaitables, return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            print(f'Got an exception {result}')


if __name__ == '__main__':
    asyncio.run(main())
