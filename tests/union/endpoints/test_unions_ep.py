import datetime

from fastapi import status
from yarl import URL

EP_URL = URL('/strikes/unions/')


async def test_unions_ep_positive(unions_batch, async_client_httpx):
    """
    Позитивный тест ЭП '/strikes/unions/' (коллекция Union). Вариант с получением
    всех записей Union.
    """
    response = await async_client_httpx.get(EP_URL.path)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data['items']) == 10

    id_to_rest = {entry['id']: entry for entry in data['items']}

    for union in unions_batch:
        entry = id_to_rest[union.id]
        assert union.id == entry['id']
        assert union.name == entry['name']
        assert union.is_yellow == entry['is_yellow']
        assert union.created_at == datetime.datetime.fromisoformat(entry['created_at'])


async def test_unions_ep_with_id(unions_batch, async_client_httpx):
    """
    Позитивный тест ЭП '/strikes/unions/' (коллекция Union). Вариант с получением
    конкретных записей по их id переданным через ГЕТ параметры.
    """
    chosen_id = unions_batch[0].id
    url = EP_URL % {'id': chosen_id}

    response = await async_client_httpx.get(str(url))

    data = response.json()
    assert len(data['items']) == 1
    assert data['items'][0]['id'] == chosen_id
