import pytest
from fastapi import Request, HTTPException
from pydantic import SecretStr

from internal.dependencies import jwt_authorize
from security.jwt import generate_jwt_token


@pytest.fixture
def fake_request() -> Request:
    """
    Типа реквест
    """
    return Request(scope={'type': 'http'})


@pytest.mark.no_db_calls
def test_jwt_authorize_positive(fake_request, db_session):
    """
    Позитивный тест зависимости jwt_authorize. Должна отдать юзера из жвт токена.
    """
    user_id = 100
    token = generate_jwt_token(user_id)
    user_id_from_token = jwt_authorize(db_session, token, fake_request, )

    assert user_id == user_id_from_token
    assert fake_request.state.user_id == user_id


@pytest.mark.no_db_calls
def test_jwt_authorize_negative(monkeypatch, fake_request, db_session):
    """
    Негативный тест зависимости jwt_authorize. Если токен скомпрометирован или истек срок его -
    то возбуждаем исключение.
    """
    user_id = 100
    token = generate_jwt_token(user_id)

    with monkeypatch.context() as m:
        m.setattr('config.settings.secret_string', SecretStr('drek'))
        with pytest.raises(HTTPException):
            jwt_authorize(db_session, token, fake_request)
