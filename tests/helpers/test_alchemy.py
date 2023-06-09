import pytest

from crud.helpers import exists_in_db
from models import User


async def test_exists_in_db_positive(db_session, user_in_db):
    """
    Позитивный тест ф-ции exists_in_db.
    """
    assert await exists_in_db(db_session, User, User.id == user_in_db.id)


@pytest.mark.no_db_calls
async def test_exists_in_db_negative(db_session):
    """
    Негативный тест ф-ции exists_in_db.
    """
    assert not await exists_in_db(db_session, User, User.id == 99999999999)
