import datetime

import factory
from pydantic import SecretStr

from internal.database import async_session
from models import User
from security.invitation import generate_invitation_token
from serializers.users import UserRegistrationSerializer

__all__ = (
    'UserInFactory',
    'UserRegistrationSerializerFactory',
)


class UserInFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Модель юзера пришедшая с фронта для создания аккаунта.
    """
    name = factory.Faker('name')
    email = factory.Faker('email')
    hashed_password = '$2b$12$uNtijERc0FMIOofs06PGCeXfA05XWKDvyZqMBe54hkf5AXJhcVu1K'

    class Meta:
        model = User


class UserRegistrationSerializerFactory(factory.Factory):
    name = factory.Faker('name')
    email = factory.Faker('email')
    password = factory.Faker('password', length=20)
    invitation_password = None

    @factory.lazy_attribute
    def invitation_token(self):
        token = generate_invitation_token(
            datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=100),
                                          )
        return SecretStr(token)

    class Meta:
        model = UserRegistrationSerializer


