from unittest.mock import patch

import pytest
from fastapi import status
from fastapi.encoders import jsonable_encoder

from crud.helpers import exists_in_db
from models import Place

EP_URL = '/strikes/places/'


@pytest.fixture
def positive_data(place_factory, faker) -> dict:
    """
    Верные данные для передачи в create_new_place для сохранения в БД с фронта.
    """
    place = place_factory.build()

    data_to_save = dict(
        name=place.name,
        address=place.address,
        coordinates=faker.latlng(),
    )
    return data_to_save


async def test_create_new_place_ep_positive(db_session,
                                            async_client_httpx,
                                            positive_data
                                            ):
    """
    Позитивный тест вью create_new_place. При передаче верных данных с фронта новый
    инстанс модели Place должен быть сохранен в БД.
    """
    response = await async_client_httpx.post(EP_URL, json=jsonable_encoder(positive_data))

    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()

    assert await exists_in_db(db_session, Place, Place.id == response_data['id'])


@patch('routers.places.create_or_update_place', side_effect=ValueError('test_error_message'))
async def test_create_new_place_ep_negative(create_place_mock, positive_data, async_client_httpx):
    """
    Негативный тест вью create_new_place. При возникновении ValueError в процессе создания
    записи в БД (координаты в радиусе 100 м от уже существующих в БД координат) отдаем 400й
    респонс с текстом исключения.
    """
    response = await async_client_httpx.post(EP_URL, json=jsonable_encoder(positive_data))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == 'test_error_message'
