import re
from typing import Annotated

from pydantic import BaseModel, Field, EmailStr, SecretStr, validator, constr

from internal.constants import USER_PASSWORD_REGEXP

__all__ = (
    'UserRegistrationSerializer',
)


password_regexp = re.compile(USER_PASSWORD_REGEXP)
password_strength_error_message = 'Password is not strong enough.'


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
        # todo
        return value
