from fastapi import status

from crud.helpers import exists_in_db
from models import Strike

EP_URL = '/strikes/{}'


async def test_update_strike_ep(db_session, strike, async_client_httpx):
    """
    Позитивный тест ЭП PATCH '/strikes/{id:int}' обновления записи Strike.
    """
    new_goals = 'test_goals_updated'
    data = dict(goals=new_goals)

    response = await async_client_httpx.patch(EP_URL.format(strike.id), json=data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['goals'] == 'test_goals_updated'
    assert await exists_in_db(
        db_session,
        Strike,
        (Strike.id == strike.id) & (Strike.goals == new_goals)
    )
