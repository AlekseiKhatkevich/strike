import re

from crud.users import create_new_user
from internal.constants import BCRYPT_REGEXP
from models import User


async def test_create_new_user_positive(db_session, user_registration_serializer_factory):
    """
    Тест ф-ции create_new_user() которая создает нового пользователя в БД.
    """
    serializer = user_registration_serializer_factory.build()
    user_from_db = await create_new_user(db_session, serializer)

    user_from_db = await db_session.get(User, user_from_db.id)

    assert user_from_db is not None
    assert re.match(BCRYPT_REGEXP, user_from_db.hashed_password) is not None
