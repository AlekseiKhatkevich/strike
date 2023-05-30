import factory
from faker import Factory as FakerFactory

from models import User

faker = FakerFactory.create()

__all__ = (
    'UserInFactory',
)


class UserInFactory(factory.alchemy.SQLAlchemyModelFactory):
    name = factory.Faker('name')
    email = factory.Faker('email')
    hashed_password = factory.Faker('password')

    class Meta:
        model = User
