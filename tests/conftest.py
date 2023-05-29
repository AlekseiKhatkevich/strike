#
#
# def pytest_generate_tests(metafunc) -> None:
#     """
#     Грузим переменные окружения.
#     https://stackoverflow.com/questions/36141024/how-to-pass-environment-variables-to-pytest
#     """
#     dotenv.load_dotenv(verbose=True)
import pytest
from fastapi.testclient import TestClient

from database import async_session
from main import app


@pytest.fixture(scope='session')
def client():
    return TestClient(app)


@pytest.fixture
def session():
    try:
        session = async_session()
        yield session
    finally:
        session.close()






