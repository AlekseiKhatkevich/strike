from sqlalchemy import MetaData, NullPool
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import uuid

from config import settings

__all__ = (
    'Base',
    'engine',
    'async_session',
)

engine = create_async_engine(
    settings.pg_dsn,
    poolclass=NullPool,
    echo=True,
    echo_pool=True,
    connect_args={
            'prepared_statement_name_func': lambda:  f'__asyncpg_{uuid.uuid4()}__',
            'server_settings': {'jit': 'off'},
            'options': '-c timezone=utc',
        },
)


async_session = async_sessionmaker(
    autocommit=False,
    bind=engine,
    expire_on_commit=False,
)


class Base(AsyncAttrs, DeclarativeBase):
    metadata = MetaData(naming_convention={
        'ix': 'ix_%(column_0_label)s',
        'uq': 'uq_%(table_name)s_%(column_0_name)s',
        'ck': 'ck_%(table_name)s_`%(constraint_name)s`',
        'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
        'pk': 'pk_%(table_name)s'
    })
