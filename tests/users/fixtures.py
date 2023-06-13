import datetime
from typing import TYPE_CHECKING

import pytest
from pytest_factoryboy import register

from internal.redis import UsersCache
from security.invitation import generate_invitation_token
from tests.factories.auth import UsedTokenFactory
from tests.factories.users import (
    UserInFactory,
    UserRegistrationSerializerFactory,
    UserInDbFactory,
)

if TYPE_CHECKING:
    from models.users import User
    from models.auth import UsedToken


@pytest.fixture
def users_cache() -> UsersCache:
    """
    Отдает экз. кл. кеша юзеров.
    """
    return UsersCache(only_active=True)


@pytest.fixture
async def user_in_redis_cache(user_in_db, users_cache) -> 'User':
    """
    Сохраняет юзера в кеше редиса.
    """
    await users_cache._add_user_into_redis(user_in_db)
    return user_in_db


@pytest.fixture
async def user_in_db(db_session, user_in_db_factory) -> 'User':
    """
    Созданная в БД запись юзера.
    """
    user = user_in_db_factory.build()
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
def invitation_token(faker) -> str:
    """
    JVT токен приглашения.
    """
    future_dt = faker.future_datetime(tzinfo=datetime.UTC)
    return generate_invitation_token(future_dt)


@pytest.fixture
async def used_token_in_db(user_in_db, db_session, used_token_factory) -> 'UsedToken':
    """
    Создаем в БД использованный токен и ассоциированного с ним пользователя.
    """
    used_token = used_token_factory.build()
    used_token.user_id = user_in_db.id
    async with db_session.begin():
        db_session.add(used_token)
        await db_session.commit()

    return used_token


register(UserInFactory)
register(UserRegistrationSerializerFactory)
register(UsedTokenFactory)
register(UserInDbFactory)
