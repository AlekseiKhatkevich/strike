import asyncio
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Annotated

from pydantic import BaseModel, Field, EmailStr, SecretStr, validator, constr

from crud.users import check_password_commonness
from internal.constants import USER_PASSWORD_REGEXP

__all__ = (
    'UserRegistrationSerializer',
)

from internal.database import async_session

password_regexp = re.compile(USER_PASSWORD_REGEXP)
password_strength_error_message = 'Password is not strong enough.'
password_commonness_error_message = 'Password is common hence weak.'


class UserRegistrationSerializer(BaseModel):
    """
    Для первоначального создания юзера через апи.
    """
    name: constr(max_length=64)
    email: EmailStr | None
    password: Annotated[SecretStr, Field(max_length=72)]
    invitation_token: SecretStr
    invitation_password: SecretStr | None

    class Config:
        anystr_strip_whitespace = True
        min_anystr_length = 1
        frozen = True

    @validator('password')
    def password_strength(cls, value: SecretStr) -> SecretStr:
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

    @validator('password')
    def password_commonness(cls, value: SecretStr) -> SecretStr:
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

