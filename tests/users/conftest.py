import pytest
from pytest_factoryboy import register
from typing import TYPE_CHECKING
from tests.factories.users import *

if TYPE_CHECKING:
    from models.users import User


@pytest.fixture
async def user_in_db(db_session, user_in_factory) -> 'User':
    """
    Созданная в БД запись юзера.
    """
    async with db_session.begin():
        user = user_in_factory.build()
        db_session.add(user)
        return user


register(UserInFactory)
