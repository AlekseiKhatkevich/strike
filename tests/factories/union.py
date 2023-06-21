import factory

from internal.database import async_session
from models import Union
from tests.factories.async_helpers import AsyncSQLAlchemyModelFactory

__all__ = (
    'UnionFactory',
)


class UnionFactory(AsyncSQLAlchemyModelFactory):
    """
    Фабрика модели Union (профсоюз).
    """
    name = factory.Faker('company')
    is_yellow = False

    class Meta:
        model = Union
        sqlalchemy_session = async_session()
        sqlalchemy_session_persistence = 'commit'
