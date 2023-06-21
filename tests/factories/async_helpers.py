import factory
from factory.alchemy import SESSION_PERSISTENCE_FLUSH, SESSION_PERSISTENCE_COMMIT
import asyncio


__all__ = (
    'AsyncSQLAlchemyModelFactory',
)


class SqlAlchemyAsyncMixin:
    """
    Миксин для сохранения фабрик в БД с asyncpg.
    """
    @classmethod
    async def _create(cls, model_class, *args, **kwargs):
        """Create an instance of the model, and save it to the database."""
        session = cls._meta.sqlalchemy_session

        if session is None:
            raise RuntimeError("No session provided.")
        if cls._meta.sqlalchemy_get_or_create:
            return cls._get_or_create(model_class, session, args, kwargs)
        return await cls._save(model_class, session, args, kwargs)

    @classmethod
    async def _save(cls, model_class, session, args, kwargs):
        obj = model_class(*args, **kwargs)
        session.add(obj)
        await cls._do_persist(session)
        return obj

    @classmethod
    async def create_batch(cls, size, **kwargs):
        instances = cls.build_batch(size, **kwargs)
        session = cls._meta.sqlalchemy_session
        session.add_all(instances)
        await cls._do_persist(session)
        return instances

    @classmethod
    async def _do_persist(cls, session):
        session_persistence = cls._meta.sqlalchemy_session_persistence
        if session_persistence == SESSION_PERSISTENCE_FLUSH:
            await session.flush()
        elif session_persistence == SESSION_PERSISTENCE_COMMIT:
            await session.commit()


class AsyncSQLAlchemyModelFactory(SqlAlchemyAsyncMixin, factory.alchemy.SQLAlchemyModelFactory):
    """
    Субкласс SQLAlchemyModelFactory для сохранения фабрик в БД с asyncpg.
    """
    pass
