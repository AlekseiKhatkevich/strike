from pathlib import Path

from sqlalchemy import func

from config import settings
from models import CommonPassword
from models.initial_data.populate_common_passwords import populate, tmp_file_path


async def test_populate_common_passwords(monkeypatch, db_session, capsys):
    """
    1) Записываем пароли в таблицу CommonPassword.
    2) Если таблица не пустая, то запись должна не начаться.
    """
    original_file_path = 'models.initial_data.populate_common_passwords.data_file_path'
    test_file_path = settings.root_path / Path('tests/fake_initial_data/10_common_passwords.txt')
    monkeypatch.setattr(original_file_path, test_file_path)

    await populate()

    assert await db_session.scalar(func.count(CommonPassword.id)) == 10

    await populate()

    captured = capsys.readouterr()
    assert 'There are data already in the table. Aborting!!!' in captured.out
    assert await db_session.scalar(func.count(CommonPassword.id)) == 10

    assert not tmp_file_path.exists()
