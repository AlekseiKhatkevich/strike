from fastapi import status

from crud.helpers import exists_in_db
from models import User

EP_URl = '/users/me/'


async def test_users_me_ep_positive(user_in_db, async_client_httpx):
    """
    Тест эндпойнта users/me который отдает данные о текущем юзере.
    """
    expected_response_json = dict(
        id=user_in_db.id,
        name=user_in_db.name,
        registration_date=user_in_db.registration_date.isoformat().replace('+00:00', 'Z'),
        email=user_in_db.email,
        is_active=user_in_db.is_active,
    )

    response = await async_client_httpx.get(EP_URl)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response_json


async def test_user_me_delete(user_in_db, async_client_httpx, db_session):
    """
    Тест эндпойнта users/me через DELETE. Удаление текущего юзера.
    """
    response = await async_client_httpx.delete(EP_URl)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not await exists_in_db(db_session, User, User.id == user_in_db.id)


async def test_user_me_update(user_in_db, async_client_httpx, db_session):
    """
    Позитивный тест эндпойтна  PUT /me/, который обновляет данные текущего юзера.
    """
    new_user_data = {'name': 'new_test_name', 'email': 'hardcase@inbox.ru', 'is_active': True}

    response = await async_client_httpx.put(EP_URl, json=new_user_data)

    assert response.status_code == status.HTTP_200_OK
    assert await exists_in_db(
        db_session,
        User,
        (User.id == user_in_db.id) & (User.name == new_user_data['name']) &
        (User.email == new_user_data['email']) & (User.is_active == new_user_data['is_active'])
    )
