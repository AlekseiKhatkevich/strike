import pytest
from fastapi import status
from yarl import URL
from main import app
# from internal.dependencies import get_session, get_db_session_test
#
# app.dependency_overrides[get_session] = get_db_session_test

EP_URL = URL('/users/')


@pytest.fixture
def positive_post_data(user_registration_serializer_factory):
    serializer = user_registration_serializer_factory.build()
    post_data = serializer.dict()
    post_data['invitation_token'] = post_data['invitation_token'].get_secret_value()
    post_data['password'] = post_data['password'].get_secret_value()
    return post_data


def test_register_new_user_positive(client, positive_post_data):
    """

    """
    response = client.post(EP_URL.path, json=positive_post_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['id']


# async def test_register_new_user_negative(client, positive_post_data):
#     """
#
#     """
#     for _ in range(2):
#         response = client.post(EP_URL.path, json=positive_post_data)
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert response.json()['detail'] == 'User with this name or email already exists'
