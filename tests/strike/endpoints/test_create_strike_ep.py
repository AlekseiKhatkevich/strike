from fastapi import status

from crud.helpers import exists_in_db
from models import Strike

EP_URL = '/strikes/'


async def test_create_strike_ep_positive(async_client_httpx, db_session, strike_input_data, faker):
    """
    Позитивный тест ЭП POST '/strikes/' создания записи Strike.
    """
    strike_input_data['duration'] = None
    strike_input_data['planned_on_date'] = faker.date()
    response = await async_client_httpx.post(EP_URL, json=strike_input_data)

    assert response.status_code == status.HTTP_201_CREATED
    resp_data = response.json()

    assert await exists_in_db(db_session, Strike, Strike.id == resp_data['id'])
