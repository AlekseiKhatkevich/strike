import factory

from models import Region
from models.initial_data import RU_regions

__all__ = (
    'RegionFactory',
)


class RegionFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Фабрика модели Region (регион РФ).
    """
    name = factory.Faker('random_element', elements=RU_regions.names)

    class Meta:
        model = Region
