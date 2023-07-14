from fastapi import status

GROUP_EP = '/strikes/{}/group'
PLACES_EP = '/strikes/{}/places'
USERS_INVOLVED_EP = '/strikes/{}/users_involved'


async def test_manage_group_ep(strike, strike_p, async_client_httpx):
    """
    Позитивный тест ЭП POST /strikes/{strike_id:int}/group.
    """
    strike_with_group = await strike_p(num_group=1)
    strike_to_add = strike
    add = [strike_to_add.id, ]
    remove = [g_strike.id for g_strike in strike_with_group.group]
    input_data = dict(add=add, remove=remove)

    response = await async_client_httpx.post(
        GROUP_EP.format(strike_with_group.id),
        json=input_data,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == add


async def test_manage_places_ep(strike, place, async_client_httpx):
    """
    Позитивный тест ЭП POST /strikes/{strike_id:int}/places.
    """
    add = [place.id, ]
    remove = [place.id for place in strike.places]
    input_data = dict(add=add, remove=remove)

    response = await async_client_httpx.post(
        PLACES_EP.format(strike.id),
        json=input_data,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == add


async def test_manage_users_involved_ep(strike, async_client_httpx, user_in_db, user_role):
    """
    Позитивный тест ЭП POST /strikes/{strike_id:int}/users_involved.
    """
    add = [{'user_id': user_in_db.id, 'role': user_role.value}, ]
    remove = [user.user_id for user in strike.users_involved]
    input_data = dict(add=add, remove=remove)

    response = await async_client_httpx.post(
        USERS_INVOLVED_EP.format(strike.id),
        json=input_data,
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            'user_id': user_in_db.id,
            'role': user_role.value,
        }
    ]
