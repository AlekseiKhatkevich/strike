import factory
from models import Jail


__all__ = (
    'JailFactory',
    'DetentionFactory',
)


class JailFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Фабрика крытой.
    """
    id = None
    name = factory.Faker('company', locale='ru_RU')
    address = factory.Faker('address', locale='ru_RU')
    region = factory.SubFactory('tests.factories.region.RegionFactory')

    class Meta:
        model = Jail


class DetentionFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Фабрика похищения человека мусарами.
    """