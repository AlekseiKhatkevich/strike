from fastapi import status

from crud.helpers import exists_in_db
from models import Union

EP_URL = '/strikes/unions/'


async def test_create_or_update_union_ep_create_positive(db_session, faker, async_client_httpx):
    """
    Позитивный тест ЭП create_or_update_union_ep. Создание записи Union.
    """
    data = {'name': faker.company()}

    response = await async_client_httpx.post(EP_URL, json=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert await exists_in_db(db_session, Union, Union.id == response.json()['id'])


async def test_create_or_update_union_ep_update_positive(db_session, union, faker, async_client_httpx):
    """
    Позитивный тест ЭП create_or_update_union_ep. Обновление записи Union.
    """
    new_name = faker.company()
    data = {'name': new_name, 'id': union.id}

    response = await async_client_httpx.put(EP_URL, json=data)

    assert response.status_code == status.HTTP_200_OK
    assert await exists_in_db(
        db_session,
        Union,
        (Union.id == response.json()['id']) & (Union.name == new_name)
    )


async def test_create_or_update_union_ep_update_negative(faker, async_client_httpx):
    """
    Негативный тест ЭП create_or_update_union_ep. Обновление записи Union. Такого id нет.
    """
    data = {'name': faker.company(), 'id': 999999}

    response = await async_client_httpx.put(EP_URL, json=data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'Union with id=999999 is not exists.'
