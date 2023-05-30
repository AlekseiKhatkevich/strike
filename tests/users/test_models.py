import datetime

import pytest
from email_validator import EmailSyntaxError
from sqlalchemy import exc as so_exc, insert

from models import User


async def test_user_model_creation_positive(db_session, user_in_factory):
    """

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
    expected_error_message = 'The email address is not valid. It must have exactly one @-sign.'
    with pytest.raises(EmailSyntaxError, match=expected_error_message):
        user_in_factory.build(email='nonsense')


async def test_user_model_email_check_constraint_negative(db_session):
    with pytest.raises(so_exc.IntegrityError):
        async with db_session.begin():
            stmt = insert(User).values(
                name='test',
                email='test',
                hashed_password='test',
            )
            await db_session.execute(stmt)


async def test_updated_at_positive(db_session, user_in_db):
    async with db_session.begin():
        user_in_db.name = 'test'
        await db_session.commit()

    async with db_session.begin():
        await db_session.refresh(user_in_db)

        await user_in_db.awaitable_attrs.updated_at
        assert user_in_db.updated_at is not None


def test_ping(client):
    response = client.get('/users/ping/')
    assert response.status_code == 200
    assert response.json() == {"ping": "pong!"}
