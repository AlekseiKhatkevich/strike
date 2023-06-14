import asyncio
import datetime
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Annotated

from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    SecretStr,
    validator,
    constr,
)

from crud.auth import check_password_commonness
from internal.constants import USER_PASSWORD_REGEXP
from internal.database import async_session

__all__ = (
    'UserRegistrationSerializer',
    'UserOutMeSerializer',
    'UserInModificationSerializer',
)


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
    email: EmailStr | None
    is_active: bool

    class Config:
        orm_mode = True


class UserBaseSerializer(BaseModel):
    """

    """
    name: constr(max_length=64)
    password: Annotated[SecretStr, Field(max_length=72)]
    email: EmailStr | None

    class Config:
        anystr_strip_whitespace = True
        min_anystr_length = 1
        frozen = True

    @validator('password', allow_reuse=True)
    def password_strength(cls, value: SecretStr | None) -> SecretStr | None:
        """
        Проверка пароля на минимально допустимую сложность.
        """
        # if value is None:
        #     return value
        password = value.get_secret_value()
        match = password_regexp.match(password)
        if match is None:
            raise ValueError(
                password_strength_error_message,
            )
        return value

    @validator('password', allow_reuse=True)
    def password_commonness(cls, value: SecretStr | None) -> SecretStr | None:
        """
        Проверка пароля по базе самых распространенных паролей.
        """
        # if value is None:
        #     return value

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
    password: Annotated[SecretStr, Field(max_length=72)] | None
    is_active: bool


class UserRegistrationSerializer(UserBaseSerializer):
    """
    Для первоначального создания юзера через апи.
    """
    invitation_token: SecretStr
    invitation_password: SecretStr | None
