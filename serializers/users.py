import asyncio
import datetime
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Annotated

from pydantic import (
    field_validator,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
    constr,
)

from crud.auth import check_password_commonness
from internal.constants import USER_PASSWORD_REGEXP
from internal.database import async_session
from internal.serializers import BaseModel

__all__ = (
    'UserRegistrationSerializer',
    'UserOutMeSerializer',
    'UserInModificationSerializer',
    'UserStatisticsSerializer',
)

from serializers.typing import IntIdType

password_regexp = re.compile(USER_PASSWORD_REGEXP)
password_strength_error_message = 'Password is not strong enough.'
password_commonness_error_message = 'Password is common hence weak.'


class UserOutMeSerializer(BaseModel):
    """
    Для отдачи основных данных юзера.
    """
    id: int
    name: str
    registration_date: datetime.datetime
    email: EmailStr | None = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserBaseSerializer(BaseModel):
    """
    Базовый сериалайзер юзера.
    """
    name: constr(max_length=64)
    password: Annotated[SecretStr, Field(max_length=72)]
    email: EmailStr | None = None

    model_config = ConfigDict(str_strip_whitespace=True, str_min_length=1, frozen=True)

    # noinspection PyNestedDecorators
    @field_validator('password')
    @classmethod
    def password_strength(cls, value: SecretStr | None) -> SecretStr | None:
        """
        Проверка пароля на минимально допустимую сложность.
        """
        password = value.get_secret_value()
        match = password_regexp.match(password)
        if match is None:
            raise ValueError(
                password_strength_error_message,
            )
        return value

    # noinspection PyNestedDecorators
    @field_validator('password')
    @classmethod
    def password_commonness(cls, value: SecretStr | None) -> SecretStr | None:
        """
        Проверка пароля по базе самых распространенных паролей.
        """
        async def _check() -> bool:
            async with async_session() as session:
                return await check_password_commonness(session, value.get_secret_value())

        with ThreadPoolExecutor(max_workers=1) as pool:
            is_common = pool.submit(asyncio.run, _check()).result()

        if is_common:
            raise ValueError(
                password_commonness_error_message,
            )
        return value


class UserInModificationSerializer(UserBaseSerializer):
    """
    Для изменения данных юзера.
    """
    email: EmailStr | None = Field(...)
    password: Annotated[SecretStr, Field(max_length=72)] | None = None
    is_active: bool


class UserRegistrationSerializer(UserBaseSerializer):
    """
    Для первоначального создания юзера через апи.
    """
    invitation_token: SecretStr
    invitation_password: SecretStr | None = None


class LogActionSerializer(BaseModel):
    """

    """
    count: IntIdType | None = None
    rank: IntIdType | None = None


class UserStatisticsSerializer(BaseModel):
    """

    """
    user_id: IntIdType
    create: LogActionSerializer = LogActionSerializer()
    update: LogActionSerializer = LogActionSerializer()
    delete: LogActionSerializer = LogActionSerializer()
    add: LogActionSerializer = LogActionSerializer()
    remove: LogActionSerializer = LogActionSerializer()
    num_strikes_created: int | None = None
    strikes_involved_ids: list[int] | None = None
    # strikes_involved_ids_active: list[int] | None

    model_config = ConfigDict(from_attributes=True)

