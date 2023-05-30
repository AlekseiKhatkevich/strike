import pytest
from pytest_factoryboy import register

from tests.factories.users import *

register(UserInFactory)


@pytest.fixture
async def user_in_db(db_session, user_in_factory):
    async with db_session.begin():
        user = user_in_factory.build()
        db_session.add(user)
        return user
