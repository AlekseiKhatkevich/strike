import datetime

import pytest
from fastapi import status
from sqlalchemy import select
from yarl import URL

from models import User
from security.invitation import generate_invitation_token

EP_URL = URL('/users/')


@pytest.fixture
def positive_post_data(user_registration_serializer_factory):
    serializer = user_registration_serializer_factory.build()
    post_data = serializer.dict()
    post_data['invitation_token'] = post_data['invitation_token'].get_secret_value()
    post_data['password'] = post_data['password'].get_secret_value()
    return post_data


async def test_register_new_user_positive(positive_post_data, async_client_httpx):
    """

    """
    response = await async_client_httpx.post(EP_URL.path, json=positive_post_data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['id']


# async def test_register_new_user_negative(async_client_httpx, positive_post_data,
#                                           user_in_db, db_session):
#     """
#
#     """
#     stmt = select(User.id).limit(1)
#     result = await db_session.scalars(stmt)
#     item = result.first()
#     assert item is not None
#
#     post_data = dict(
#         name=user_in_db.name,
#         email=user_in_db.email,
#         password='1Q2w3e(*)*)KSHJDIOSDeeee',
#         invitation_token=generate_invitation_token(datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(days=100))
#     )
#
#     response = await async_client_httpx.post(EP_URL.path, json=post_data)
#     assert response.status_code == status.HTTP_400_BAD_REQUEST
#     assert response.json()['detail'] == 'User with this name or email already exists'
