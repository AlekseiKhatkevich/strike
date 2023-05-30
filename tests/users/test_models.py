import datetime

import pytest
from email_validator import EmailSyntaxError
from sqlalchemy import exc as so_exc, insert

from models import User


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


async def test_user_model_email_check_constraint_negative(db_session):
    """
    Негативный тест чек констрейнта на поле email. Используем SA.insert так как в таком случае
    валидация модели не срабатывает.
    """
    with pytest.raises(so_exc.IntegrityError):
        async with db_session.begin():
            stmt = insert(User).values(
                name='test',
                email='test',
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
