import datetime
import uuid

from sqlalchemy import (
    BigInteger,
    TIMESTAMP,
    MetaData,
    NullPool,
)
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config import settings
from internal.typing_and_types import BigIntType

__all__ = (
    'Base',
    'engine',
    'async_session',
)


engine = create_async_engine(
    settings.pg_dsn,
    poolclass=NullPool,
    echo=settings.debug,
    echo_pool=settings.debug,
    connect_args={
            'prepared_statement_name_func': lambda: f'__asyncpg_{uuid.uuid4()}__',
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
        'ck': 'ck_%(table_name)s_%(constraint_name)s',
        'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
        'pk': 'pk_%(table_name)s'
    })
    type_annotation_map = {
        BigIntType: BigInteger,
        datetime.datetime: TIMESTAMP(timezone=True),
    }
