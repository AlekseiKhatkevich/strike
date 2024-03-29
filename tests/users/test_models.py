import datetime

import pytest
from email_validator import EmailSyntaxError
from sqlalchemy import exc as so_exc, insert, select

from models import User, CommonPassword, UsedToken
from security.hashers import make_hash


async def test_user_model_creation_positive(db_session, user_in_factory):
    """
    Позитивный тест создания записи в БД в случае сохранения модели User c корректными данными.
    """
    async with db_session.begin():
        user = user_in_factory.build()
        db_session.add(user)

    async with db_session.begin():
        await db_session.refresh(user)
        assert user.id is not None

        await user.awaitable_attrs.hashed_password
        await user.awaitable_attrs.updated_at

        assert user.is_active
        assert user.updated_at is None
        assert user.registration_date.tzinfo == datetime.UTC


def test_user_model_email_validator_negative(user_in_factory):
    """
    Негативный тест валидатора SA на поле email.
    """
    expected_error_message = 'The email address is not valid. It must have exactly one @-sign.'
    with pytest.raises(EmailSyntaxError, match=expected_error_message):
        user_in_factory.build(email='nonsense')


@pytest.mark.parametrize('field, value', [('email', 'wrong_email'), ('hashed_password', 'wrong_hp')])
async def test_user_model_email_check_constraint_negative(db_session, field, value):
    """
    Тесты чек констренйтов модели User.
    """
    data = dict(
        name='test',
        email='qw@email.com',
        hashed_password=make_hash('password'),
    )
    data[field] = value

    with pytest.raises(so_exc.IntegrityError):
        async with db_session.begin():
            stmt = insert(User).values(
                **data
            )
            await db_session.execute(stmt)


async def test_user_model_hashed_password_check_constraint_negative(db_session):
    """

    """
    with pytest.raises(so_exc.IntegrityError):
        async with db_session.begin():
            stmt = insert(User).values(
                name='test',
                email='qwerty12345@email.com',
                hashed_password='test',
            )
            await db_session.execute(stmt)


async def test_updated_at_positive(db_session, user_in_db):
    """
    Позитивный тест обновления записи модели User. В поле updated_at должен записаться текущий datetime.
    """
    async with db_session.begin():
        user_in_db.name = 'test'
        await db_session.commit()

    async with db_session.begin():
        await db_session.refresh(user_in_db)

        await user_in_db.awaitable_attrs.updated_at
        assert user_in_db.updated_at is not None

#  //  CommonPassword


async def test_common_password_positive(db_session):
    """
    Позитивный тест модели "CommonPassword"
    """
    password_example = '1q2w3e'
    async with db_session.begin():
        db_session.add(CommonPassword(password=password_example))

    stmt = select(CommonPassword.id).where(CommonPassword.password == password_example).limit(1)
    assert bool(await db_session.scalar(stmt))

#  // UserToken


async def test_user_token_positive(used_token_in_db, db_session):
    """
    Сохраняется ли использованный токен в БД.
    """
    token_from_db = await db_session.get(UsedToken, used_token_in_db.id)
    assert token_from_db.user_id is not None
