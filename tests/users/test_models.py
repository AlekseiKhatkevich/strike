import os

import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_mani(session):
    async with session.begin():
        a = await session.execute(text('select version()'))
        assert 1 + 1 == 2
        assert os.environ['SECRET_STRING'] == 'fake_secret_string'
