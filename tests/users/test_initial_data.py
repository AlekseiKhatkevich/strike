import pytest
from pathlib import Path
from sqlalchemy import func, select
from config import settings

from models import CommonPassword
from models.initial_data.populate_common_passwords import populate

# приджоинить
# сессию замонкипатчить


async def test_populate_common_passwords_positive(monkeypatch, db_session):
    """

    """
    original_file_path = 'models.initial_data.populate_common_passwords.data_file_path'
    test_file_path = settings.root_path / Path('tests/fake_initial_data/10_common_passwords.txt')
    monkeypatch.setattr(original_file_path, test_file_path)

    await populate()

    assert await db_session.scalar(func.count(CommonPassword.id)) == 10


