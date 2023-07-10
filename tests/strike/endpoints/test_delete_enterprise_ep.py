from fastapi import status

from crud.helpers import is_instance_in_db

EP_URL = 'strikes/{}'


async def test_delete_strike_ep(async_client_httpx, db_session, strike):
    """
    Позитивный тест ЭП DELETE strikes/{id:int} удаления записи Strike.
    """
    response = await async_client_httpx.delete(EP_URL.format(strike.id))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not await is_instance_in_db(db_session, strike)
