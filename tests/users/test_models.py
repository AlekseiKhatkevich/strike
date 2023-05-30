import os

import pytest
from sqlalchemy import text, insert

from models import User


async def test_mani(db_session):

    async with db_session.begin():
        stmt = insert(User).values(
            name='test',
            email='hardcase@inbox.ru',
            hashed_password='sdfsdfdsf',
        )
        db_response = await db_session.execute(stmt)
    assert os.environ['SECRET_STRING'] == 'fake_secret_string'


def test_ping(client):
    response = client.get('/users/ping/')
    assert response.status_code == 200
    assert response.json() == {"ping": "pong!"}
