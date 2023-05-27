import re
from typing import Annotated

from pydantic import BaseModel, Field, EmailStr, SecretStr, validator

from constants import USER_PASSWORD_REGEXP

__all__ = (
    'UserRegistrationSerializer',
)


password_regexp = re.compile(USER_PASSWORD_REGEXP)
password_strength_error_message = 'Password is not strong enough.'


class UserRegistrationSerializer(BaseModel):
    name: Annotated[str, Field(max_length=64)]
    email: Annotated[EmailStr | None, Field()]
    password: Annotated[SecretStr, Field(max_length=32, min_length=12,)]

    class Config:
        anystr_strip_whitespace = True
        min_anystr_length = 1
        frozen = True

    @validator('password')
    def password_strength(cls, value: SecretStr) -> SecretStr:
        password = value.get_secret_value()
        match = password_regexp.match(password)
        if match is None:
            raise ValueError(
                password_strength_error_message,
            )
        return value




