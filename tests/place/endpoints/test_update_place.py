from fastapi import status

from crud.helpers import exists_in_db
from models import Place

EP_URL = '/strikes/places/'


async def test_update_place_ep_positive(db_session, async_client_httpx, place):
    """
    Позитивный тест '/strikes/places/' вариант с обновлением записи Place через PUT / PATCH.
    """
    data_to_update = dict(
        id=place.id,
        address='new_test_address',
        coordinates=None,
        name=place.name,
    )

    response = await async_client_httpx.put(EP_URL, json=data_to_update)

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()

    assert response_data['address'] == data_to_update['address']

    assert await exists_in_db(
        db_session,
        Place,
        (Place.id == place.id) & (Place.address == data_to_update['address']) &
        (Place.coordinates == data_to_update['coordinates'])
    )
