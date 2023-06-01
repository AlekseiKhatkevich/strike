import contextlib
import datetime
from typing import TYPE_CHECKING

import jwt

from config import settings

if TYPE_CHECKING:
    from pydantic import SecretStr

__all__ = (
    'generate_invitation_token',
    'verify_invitation_token',
    'InvitationTokenDeclinedException',
)

ALL_USERS = '__ALL__'
ALGORYTHM = 'HS256'


class InvitationTokenDeclinedException(Exception):
    """
    Общее исключение связанное с неправильностью токена приглашения.
    """
    text = 'Invitation token was declined.'


def generate_invitation_token(valid_util: datetime.datetime,
                              for_username_only: str = None,
                              invitation_password: str = None,
                              ) -> str:
    """
    Создать токен приглашения юзера к регистрации.
    :param valid_util: До какого момента токен считается действительным.
    :param for_username_only: Можно ограничить username для которого будет действительным токен. Не обязателен.
    :param invitation_password: Пароль для токена. Не обязателен.
    :return: Токен приглашения в формате JWT
    """
    if valid_util.tzinfo is None:
        raise ValueError('Valid until should be TZ aware!')

    payload = dict(
        exp=valid_util.timestamp(),
        iss='strike:invitation',
        iat=datetime.datetime.now(tz=datetime.UTC).timestamp(),
        aud=for_username_only or ALL_USERS,
    )

    if invitation_password is not None:
        payload['invitation_password'] = invitation_password

    return jwt.encode(payload, settings.secret_string.get_secret_value(), algorithm=ALGORYTHM)


def verify_invitation_token(token: 'SecretStr', username: str = None, password: 'SecretStr' = None) -> dict:
    """

    :param token: Токен авторизации.
    :param username: Имя пользователя.
    :param password: Пароль токена.
    :return: Расшифрованный токен в формате JWT
    """
    try:
        decoded = jwt.decode(
            token.get_secret_value(),
            settings.secret_string.get_secret_value(),
            audience=[username, ALL_USERS],
            algorithms=ALGORYTHM,
        )
    except (jwt.InvalidAudienceError, jwt.ExpiredSignatureError, jwt.InvalidSignatureError) as err:
        # todo logging
        raise InvitationTokenDeclinedException() from err

    with contextlib.suppress(KeyError):
        invitation_password = decoded['invitation_password']
        if invitation_password != password.get_secret_value():
            # todo logging
            raise InvitationTokenDeclinedException()

    return decoded

