from fastapi import status


EP_URL = '/detentions/statistics/daily/'


async def test_daily_stats_ep_positive(async_client_httpx, detentions_for_view):
    """
    Позитивный тест ЭП '/detentions/statistics/daily/' статистики по дням.
    """
    jail1, jail2, detentions_jail1, detentions_jail2 = detentions_for_view

    response = await async_client_httpx.get(EP_URL)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()['items']
    assert len(data) == 4

    assert data[0]['date'] == detentions_jail2[0].duration.upper.date().isoformat()
    assert data[0]['jail_id'] == jail2.id
    assert data[0]['zk_count'] == len(detentions_jail2)

    assert data[1]['date'] == detentions_jail2[0].duration.lower.date().isoformat()
    assert data[1]['jail_id'] == jail2.id
    assert data[1]['zk_count'] == len(detentions_jail2)

    assert data[2]['date'] == detentions_jail1[0].duration.upper.date().isoformat()
    assert data[2]['jail_id'] == jail1.id
    assert data[2]['zk_count'] == len(detentions_jail1)

    assert data[3]['date'] == detentions_jail1[0].duration.lower.date().isoformat()
    assert data[3]['jail_id'] == jail1.id
    assert data[3]['zk_count'] == len(detentions_jail1)
