from fastapi import status

from crud.helpers import is_instance_in_db

EP_URL = '/strikes/enterprises/{}/'


async def test_delete_enterprise_ep(db_session,
                                    async_client_httpx,
                                    enterprise_instance,
                                    ):
    """
    Позитивный тест эндпойнта удаления Enterprise DElETE '/strikes/enterprises/{id}/'
    """
    response = await async_client_httpx.delete(EP_URL.format(enterprise_instance.id))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not await is_instance_in_db(db_session, enterprise_instance)
