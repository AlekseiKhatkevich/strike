import os

import pytest
# import dependencies
import dotenv


# from database import async_session


__all__ = (
    'get_session'
)


# @pytest.fixture
# async def get_session():
#     async with async_session() as _session:
#         yield _session


# get_session = pytest.fixture(dependencies.get_session)


def pytest_generate_tests(metafunc) -> None:
    """
    Грузим переменные окружения.
    https://stackoverflow.com/questions/36141024/how-to-pass-environment-variables-to-pytest
    """
    dotenv.load_dotenv(verbose=True)
    os.environ['test'] = '228'
