from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config import settings

__all__ = (
    'Base',
    'engine',
    'async_session',
)

engine = create_async_engine(
    settings.pg_dsn,
    echo=True,
    echo_pool=True,
)


async_session = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(AsyncAttrs, DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_`%(constraint_name)s`",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })

