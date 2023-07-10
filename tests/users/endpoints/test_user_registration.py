import pytest
from fastapi import status
from yarl import URL

EP_URL = URL('/users/')


@pytest.fixture
def positive_post_data(user_registration_serializer_factory) -> dict[str, ...]:
    """
    Словарь с данными для передачи энппойнту для создания юзера.
    """
    serializer = user_registration_serializer_factory.build()
    post_data = serializer.model_dump()
    post_data['invitation_token'] = post_data['invitation_token'].get_secret_value()
    post_data['password'] = post_data['password'].get_secret_value()
    return post_data


async def test_register_new_user_positive(positive_post_data, async_client_httpx):
    """
    Позитивный тест ЭП создания юзера.
    """
    response = await async_client_httpx.post(EP_URL.path, json=positive_post_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['id']
