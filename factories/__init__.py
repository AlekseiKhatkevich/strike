import factory

from models import User

from faker import Factory as FakerFactory

faker = FakerFactory.create()

__all__ = (
    'UserFactory',
)


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    name = factory.Faker('name')
    email = factory.Faker('email')
    hashed_password = factory.Faker('password')

    class Meta:
        model = User
