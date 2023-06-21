import factory

from internal.database import async_session
from models import Enterprise

__all__ = (
    'EnterpriseFactory',
)


class EnterpriseFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Фабрика модели Enterprise (капиталистическая компания).
    """
    name = factory.Faker('company', locale='ru_RU')
    place = factory.Faker('city', locale='ru_RU')
    address = factory.Faker('street_address', locale='ru_RU')
    field_of_activity = factory.Faker('bs', locale='ru_RU')
    region = factory.SubFactory('tests.factories.region.RegionFactory')

    class Meta:
        model = Enterprise
        sqlalchemy_session = async_session()
        sqlalchemy_session_persistence = 'commit'
