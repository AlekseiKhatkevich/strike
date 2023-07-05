from fastapi import status

EP_URL = '/strikes/enterprises/'


async def test_get_enterprises_ep_positive(async_client_httpx, db_session, enterprise_factory):
    """
    Позитивный тест ЭП GET '/strikes/enterprises/' отдачи коллекции компаний.
    """
    enterprises = enterprise_factory.build_batch(size=2)
    db_session.add_all(enterprises)
    await db_session.commit()

    response = await async_client_httpx.get(EP_URL)
    assert response.status_code == status.HTTP_200_OK

    items = response.json()['items']
    assert len(items) == 2

    assert {el['id'] for el in items} == {ent.id for ent in enterprises}
    assert response.json()['total'] == 2

