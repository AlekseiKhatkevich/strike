import os

import pytest
from sqlalchemy import text




async def test_mani(db_session, event_loop):
    type(event_loop)
    async with db_session.begin():
        a = await db_session.execute(text('select version()'))
        assert 1 + 1 == 2
        assert os.environ['SECRET_STRING'] == 'fake_secret_string'


def test_ping(client):
    response = client.get('/users/ping/')
    assert response.status_code == 200
    assert response.json() == {"ping": "pong!"}
