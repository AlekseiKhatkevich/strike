import datetime

import pytest
from pydantic import SecretStr

from security.invitation import (
    generate_invitation_token,
    verify_invitation_token,
    InvitationTokenDeclinedException,
)

valid_until = datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=100)
expired = datetime.datetime.now(tz=datetime.UTC) - datetime.timedelta(days=100)


@pytest.mark.no_db_calls
def test_generate_invitation_token_positive():
    """
    Позитивный тест генерации jwt токена приглашения для регистрации юзера.
    """
    token = generate_invitation_token(valid_until)
    assert isinstance(token, str)


@pytest.mark.no_db_calls
def test_generate_invitation_token_negative():
    """
    Негативный тест генерации jwt токена приглашения для регистрации юзера.
    Переданное время без таймзоны.
    """
    with pytest.raises(ValueError, match='Valid until should be TZ aware!'):
        generate_invitation_token(valid_until.utcnow())


@pytest.mark.no_db_calls
def test_verify_invitation_token_base_positive():
    """
    Позитивный тест верификации токена.
    """
    token = generate_invitation_token(valid_until)
    verify_invitation_token(SecretStr(token))


@pytest.mark.no_db_calls
def test_verify_invitation_token_base_expired_negative():
    """
    Негативный тест верификации токена.
    Токен просрочен.
    """
    token = generate_invitation_token(expired)
    with pytest.raises(InvitationTokenDeclinedException):
        verify_invitation_token(SecretStr(token))


@pytest.mark.no_db_calls
def test_verify_invitation_token_base_wrong_secret_key_negative(monkeypatch):
    """
    Негативный тест верификации токена.
    Токен подделан или сформирован на основе какого то другого ключа.
    """
    with monkeypatch.context() as m:
        m.setattr('config.settings.secret_string', SecretStr('test'))
        token = generate_invitation_token(valid_until)

    with pytest.raises(InvitationTokenDeclinedException):
        verify_invitation_token(SecretStr(token))


@pytest.mark.no_db_calls
def test_verify_invitation_token_username_positive():
    """
    Позитивный тест верификации токена который валиден только для какого то конкретного username.
    """
    token = generate_invitation_token(valid_until, for_username_only='test')
    verify_invitation_token(SecretStr(token), username='test')


@pytest.mark.no_db_calls
def test_verify_invitation_token_username_negative():
    """
    Негативный тест верификации токена который валиден только для какого то конкретного username.
    Неправильное имя юзера по отношению к зашифрованному в токене.
    """
    token = generate_invitation_token(valid_until, for_username_only='test')
    with pytest.raises(InvitationTokenDeclinedException):
        verify_invitation_token(SecretStr(token), username='wrong')


@pytest.mark.no_db_calls
def test_verify_invitation_token_password_positive():
    """
    Позитивный тест верификации токена с дополнительно передаваемым паролем.
    """
    token = generate_invitation_token(valid_until, invitation_password='test')
    verify_invitation_token(SecretStr(token), password=SecretStr('test'))


@pytest.mark.no_db_calls
def test_verify_invitation_token_password_negative():
    """
    Негативный тест верификации токена с дополнительно передаваемым паролем.
    Пароль не верен.
    """
    token = generate_invitation_token(valid_until, invitation_password='test')
    with pytest.raises(InvitationTokenDeclinedException):
        verify_invitation_token(SecretStr(token), password=SecretStr('wrong'))
