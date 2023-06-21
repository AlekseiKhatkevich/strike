import factory
from factory.alchemy import SESSION_PERSISTENCE_FLUSH, SESSION_PERSISTENCE_COMMIT

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
        session_persistence = cls._meta.sqlalchemy_session_persistence

        obj = model_class(*args, **kwargs)
        session.add(obj)
        if session_persistence == SESSION_PERSISTENCE_FLUSH:
            await session.flush()
        elif session_persistence == SESSION_PERSISTENCE_COMMIT:
            await session.commit()
        return obj


class AsyncSQLAlchemyModelFactory(SqlAlchemyAsyncMixin, factory.alchemy.SQLAlchemyModelFactory):
    """
    Субкласс SQLAlchemyModelFactoryдля сохранения фабрик в БД с asyncpg.
    """
    pass
