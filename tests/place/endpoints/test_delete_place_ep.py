from fastapi import status

from crud.helpers import exists_in_db
from models import Place

EP_URL = '/strikes/places/'


async def test_delete_place_ep_positive(db_session, place, async_client_httpx):
    """
    Позитивный тест эндпойнта /strikes/places/ DELETE (удаление записи Place).
    """
    response = await async_client_httpx.request('DELETE', EP_URL, json={'id': place.id})

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not await exists_in_db(db_session, Place, Place.id == place.id)
