import contextvars
import datetime
import uuid
from functools import cache
from typing import Self

from sqlalchemy import (BigInteger, MetaData, NullPool, TIMESTAMP, inspect)
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import settings
from internal.typing_and_types import BigIntType

__all__ = (
    'Base',
    'engine',
    'async_session',
    'db_session_context_var',
)


engine = create_async_engine(
    settings.pg_dsn.unicode_string(),
    poolclass=NullPool,
    echo=settings.debug,
    echo_pool=settings.debug,
    connect_args={
            'prepared_statement_name_func': lambda: f'__asyncpg_{uuid.uuid4()}__',
            'timeout': 10,
        },
)
sync_maker = sessionmaker()
async_session = async_sessionmaker(
    autocommit=False,
    bind=engine,
    expire_on_commit=False,
    # autobegin=False,
    sync_session_class=sync_maker,
)

db_session_context_var: contextvars.ContextVar[AsyncSession] = contextvars.ContextVar('db_session')


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

    @classmethod
    @cache
    def get_model_by_name(cls, model_name: str) -> Self:
        """
        Получает инстанс модели по ее имени из реестра.
        """
        registry_instance = getattr(cls, 'registry')
        for mapper_ in registry_instance.mappers:
            model = mapper_.class_
            model_class_name = model.__name__
            if model_class_name == model_name:
                return model
        else:
            raise LookupError(
                f'Model with name {model_name} has not found in registry.'
            )

    @property
    def pk(self):
        pk_inst = inspect(self.__class__).primary_key
        pk_name = pk_inst[0].name
        return getattr(self, pk_name)
