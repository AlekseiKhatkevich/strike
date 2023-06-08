import datetime

import jwt

from config import settings

ALGORYTHM = 'HS256'

__all__ = (
    'generate_jwt_token',
    'validate_jwt_token',
)


def generate_jwt_token(user_id: int) -> str:
    """
    Генерирует JWT токен с user_id внутри.
    """
    now = datetime.datetime.now(tz=datetime.UTC)

    payload = dict(
        sub=user_id,
        iss='strike:auth',
        iat=now.timestamp(),
        exp=now + datetime.timedelta(minutes=settings.access_token_expire_minutes),
    )
    headers = dict(
        alg=ALGORYTHM,
        typ='JWT',
        kid='',
    )
    return jwt.encode(
        payload,
        settings.secret_string.get_secret_value(),
        algorithm=ALGORYTHM,
        headers=headers,
    )


def validate_jwt_token(token: str) -> int:
    """
    Валидирует JWT токен и возвращает user_id.
    """
    payload = jwt.decode(token, settings.secret_string.get_secret_value(), algorithms=ALGORYTHM)
    return payload['sub']
