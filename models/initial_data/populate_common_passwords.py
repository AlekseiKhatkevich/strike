import aioshutil
from aiopath import AsyncPath
from sqlalchemy import text, select

from internal.database import async_session
from models.users import CommonPassword

__all__ = (
    'populate',
)

data_file_path = AsyncPath('internal/data/10-million-password-list-top-1000000.txt')
tmp_file_path = AsyncPath('/tmp/10-million-password-list-top-1000000.txt')


async def write_data_in_db() -> None:
    """
    Проверяет есть ли записи в таблице "common_passwords". Если нет, то читает
    данные из файла и записывает их в таблицу.
    """
    async with async_session() as session:
        stmt = select(CommonPassword.id).limit(1)
        data_exists = bool(await session.scalar(stmt))

        if not data_exists:
            await session.execute(
                text(
                    f"""
                    COPY {CommonPassword.__tablename__} ({CommonPassword.password.name})
                    FROM '{tmp_file_path}';
                    """
                )
            )
            await session.commit()
            print('Done!')
        else:
            print('There are data already in the table. Aborting!!!')
        await session.close()


async def populate():
    """
    Копирует файл с паролями в /tmp, и затем запускает запись данных в таблицу из файла.
    """
    try:
        await aioshutil.copy(data_file_path, tmp_file_path)
        await write_data_in_db()
    finally:
        await tmp_file_path.unlink(missing_ok=True)
