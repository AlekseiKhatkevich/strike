import re

from sqlalchemy import insert

from crud.users import create_new_user, check_password_commonness
from internal.constants import BCRYPT_REGEXP
from models import User, CommonPassword


async def test_create_new_user_positive(db_session, user_registration_serializer_factory):
    """
    Тест ф-ции create_new_user() которая создает нового пользователя в БД.
    """
    serializer = user_registration_serializer_factory.build()
    user_from_db = await create_new_user(db_session, serializer)

    user_from_db = await db_session.get(User, user_from_db.id)

    assert user_from_db is not None
    assert re.match(BCRYPT_REGEXP, user_from_db.hashed_password) is not None


async def test_check_password_commonness_negative(db_session):
    """
    check_password_commonness должен возвращать True если пароль есть в базе распространенных
    паролей.
    """
    common_password = 'trgHH65**654gsdUY'
    async with db_session.begin():
        stmt = insert(CommonPassword).values(password=common_password)
        await db_session.execute(stmt)

    assert await check_password_commonness(db_session, common_password)


async def test_check_password_commonness_positive(db_session):
    """
    check_password_commonness должен возвращать False если пароля нет в базе распространенных
    паролей.
    """
    common_password = 'trgHH65**654gsdUY'
    assert not await check_password_commonness(db_session, common_password)
