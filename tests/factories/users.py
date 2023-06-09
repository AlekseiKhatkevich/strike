import datetime

import factory
from pydantic import SecretStr

from models import User
from security.hashers import make_hash
from security.invitation import generate_invitation_token
from serializers.users import UserRegistrationSerializer

__all__ = (
    'UserInFactory',
    'UserRegistrationSerializerFactory',
    'UserInDbFactory',
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


class UserInDbFactory(UserInFactory):
    """
    Модель юзера сохраненная в БД. Хеш сделан по известному паролю.
    """
    hashed_password = factory.lazy_attribute(
        lambda o: make_hash(o.password)
    )

    class Params:
        password = '1q2w3e'


class UserRegistrationSerializerFactory(factory.Factory):
    """
    Сериалайзер для данных получаемых от фронта при регистрации пользователя.
    """
    name = factory.Faker('name')
    email = factory.Faker('email')
    password = factory.Faker('password', length=30)
    invitation_password = factory.lazy_attribute(
        lambda o: SecretStr(o.invitation_password)
    )
    invitation_token = factory.LazyAttribute(
        lambda o: SecretStr(generate_invitation_token(o.future))
    )

    class Meta:
        model = UserRegistrationSerializer

    class Params:
        future = factory.Faker('future_datetime', tzinfo=datetime.UTC)
        invitation_password = factory.Faker('password')
