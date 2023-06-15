import re

import pytest
from pydantic import SecretStr
from sqlalchemy import insert

from crud.auth import check_password_commonness, check_invitation_token_used_already
from crud.helpers import exists_in_db
from crud.users import create_new_user, delete_user, update_user
from internal.constants import BCRYPT_REGEXP
from models import User, CommonPassword
from security.invitation import InvitationTokenDeclinedException


async def test_create_new_user_positive(db_session, user_registration_serializer_factory):
    """
    Тест ф-ции create_new_user() которая создает нового пользователя в БД.
    """
    serializer = user_registration_serializer_factory.build()
    user_from_db = await create_new_user(db_session, serializer)

    user_from_db = await db_session.get(User, user_from_db.id)

    assert user_from_db is not None
    assert re.match(BCRYPT_REGEXP, user_from_db.hashed_password) is not None


async def test_create_new_user_negative(db_session, user_registration_serializer_factory, used_token_in_db):
    """
    Негативный тест CRUD ф-ции create_new_user. В случае если пригласительный токен уже был
    использован и находится в таблице использованных токенов - возбуждаем исключение.
    """
    with pytest.raises(InvitationTokenDeclinedException):
        await create_new_user(
            db_session,
            user_registration_serializer_factory.build(invitation_token=SecretStr(used_token_in_db.token)),
        )


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


async def test_check_check_invitation_token_used_already_positive(used_token_in_db, db_session):
    """
    Если токен не был использован - то все ОК.
    """
    was_used_already = await check_invitation_token_used_already(db_session, 'test')
    assert not was_used_already


async def test_check_check_invitation_token_used_already_negative(used_token_in_db, db_session):
    """
    Если токен был уже использован - то возбуждаем исключение.
    """
    with pytest.raises(InvitationTokenDeclinedException):
        await check_invitation_token_used_already(db_session, used_token_in_db.token)


async def test_delete_user(db_session, user_in_db):
    """
    Тест ф-ции delete_user которая должна удалить юзера.
    """
    await delete_user(db_session, user_in_db)

    assert not await exists_in_db(db_session, User, User.id == user_in_db.id)


async def test_update_user(db_session, user_in_db):
    """
    Тест CRUD ф-ции update_user обновляющей юзера.
    """
    user_data = {'name': 'new_test_name'}

    new_user_instance = await update_user(db_session, user_in_db, user_data)

    assert new_user_instance.name == user_data['name']
    assert await exists_in_db(db_session, User, User.name == user_data['name'])


async def test_update_user_new_password(db_session, user_in_db, faker):
    """
    Тест CRUD ф-ции update_user обновляющей юзера. Обновляем парольюзера.
    """
    old_hashed_password = user_in_db.hashed_password
    user_data = {'password': SecretStr(faker.password())}

    new_user_instance = await update_user(db_session, user_in_db, user_data)

    assert new_user_instance.hashed_password != old_hashed_password
