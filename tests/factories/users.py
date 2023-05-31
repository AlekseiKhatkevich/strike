import factory
from faker import Factory as FakerFactory

from models import User


__all__ = (
    'UserInFactory',
)


faker = FakerFactory.create()


class UserInFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Модель юзера пришедшая с фронта для создания аккаунта.
    """
    name = factory.Faker('name')
    email = factory.Faker('email')
    hashed_password = '$2b$12$uNtijERc0FMIOofs06PGCeXfA05XWKDvyZqMBe54hkf5AXJhcVu1K'

    class Meta:
        model = User
