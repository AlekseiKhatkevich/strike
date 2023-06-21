import factory

from internal.database import async_session
from models import Region
from models.initial_data import RU_regions
from tests.factories.async_helpers import AsyncSQLAlchemyModelFactory

__all__ = (
    'RegionFactory',
)


class RegionFactory(AsyncSQLAlchemyModelFactory):
    """
    Фабрика модели Region (регион РФ).
    """
    name = factory.Faker('random_element', elements=RU_regions.names)

    class Meta:
        model = Region
        sqlalchemy_session = async_session()
        sqlalchemy_session_persistence = 'commit'
