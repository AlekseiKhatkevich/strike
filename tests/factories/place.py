import factory

from internal.geo import point_from_numeric
from models import Place

__all__ = (
    'PlaceFactory',
)


class PlaceFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Фабрика модели Place (место проведения забастовки).
    """
    name = factory.Faker('street_name', locale='ru_RU')
    address = factory.Faker('address', locale='ru_RU')
    coordinates = factory.LazyAttribute(
        lambda o: point_from_numeric(*o.coords_in_decimal)
    )

    class Meta:
        model = Place

    class Params:
        coords_in_decimal = factory.Faker('latlng')
