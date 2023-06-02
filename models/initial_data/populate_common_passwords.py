from pathlib import Path
import shutil
import tempfile

from internal.database import async_session
from sqlalchemy import text, select
from models.users import CommonPassword

data_file_path = Path('internal/data/10-million-password-list-top-1000000.txt')
tmp_file_path = Path('/tmp/10-million-password-list-top-1000000.txt')

shutil.copy(data_file_path, tmp_file_path)

async with async_session() as session:
    stmt = select(CommonPassword.id).limit(1)
    data_exists = bool(await session.scalar(stmt))

    if not data_exists:
        await session.execute(text(
            f"""
                COPY {CommonPassword.__tablename__} ({CommonPassword.password.name})
                FROM '{tmp_file_path}';
            """
            )
        )
        await session.commit()
    else:
        print('There are data already in the table. Aborting!!!')

    await session.close()
    print('Done!')

#delete tmp.file