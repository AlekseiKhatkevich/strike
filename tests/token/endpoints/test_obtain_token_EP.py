import pytest
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from models import User
from routers.token import authenticate_user_by_creds

EP_URL = '/token/'


@pytest.fixture
def form_data(faker) -> OAuth2PasswordRequestForm:
    """
    Форма с логином и паролем пришедшая с фронта.
    """
    return OAuth2PasswordRequestForm(
        username=faker.name(),
        password='1q2w3e',
        scope='scope',
    )


async def test_authenticate_user_by_creds_dependency_positive(db_session, user_in_db, form_data):
    """
    Позитивный тест зависимости authenticate_user_by_creds. Если логин и пароль верны – то должна
    отдавать юзера.
    """
    form_data.username = user_in_db.name

    authenticated_user = await authenticate_user_by_creds(db_session, form_data)

    assert authenticated_user is user_in_db


async def test_authenticate_user_by_creds_dependency_negative(db_session):
    """
    Негативный тест зависимости authenticate_user_by_creds. Если юзер не существует или логин
    или пароль не верен - то возбуждаем исключение.
    """
    expected_error_message = 'Could not validate credentials'
    form_data = OAuth2PasswordRequestForm(
        username='fake_name',
        password='1q2w3e',
        scope='scope',
    )

    with pytest.raises(HTTPException) as err:
        await authenticate_user_by_creds(db_session, form_data)
        assert err.status_code == status.HTTP_401_UNAUTHORIZED
        assert err.detail == expected_error_message


async def test_obtain_toke_ep_positive(user_in_db, async_client_httpx, db_session, client):
    """

    """
    post_data = dict(
        username=user_in_db.name,
        password='1q2w3e',
    )

    user = await db_session.get(User, user_in_db.id)
    assert user is not None
    print(user, 'here228')


    response = await async_client_httpx.post(EP_URL, data=post_data)

    assert response.status_code == status.HTTP_200_OK


