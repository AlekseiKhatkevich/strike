import pytest
from fastapi import status

from security.jwt import generate_jwt_token

EP_URl = '/users/me/'


@pytest.fixture
def auth_header(user_in_db):
    return {
        'Authorization': f'Bearer {generate_jwt_token(user_in_db.id)}'
    }


async def test_users_me_ep_positive(user_in_db, async_client_httpx, auth_header):
    """
    Тест эндпойнта users/me который отдает данные о текущем юзере.
    """
    expected_response_json = dict(
        id=user_in_db.id,
        name=user_in_db.name,
        registration_date=user_in_db.registration_date.isoformat(),
        email=user_in_db.email,
        is_active=user_in_db.is_active,
    )

    response = await async_client_httpx.get(EP_URl, headers=auth_header)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response_json
