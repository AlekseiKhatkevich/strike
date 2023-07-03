from fastapi import status
from yarl import URL

from crud.helpers import is_instance_in_db

EP_URL = URL('/strikes/unions/')


async def test_delete_union_ep_positive(db_session, async_client_httpx, union):
    """
    Позитивный тест ЭП DELETE /strikes/unions/ удаление записи union из БД.
    """
    response = await async_client_httpx.delete(str(EP_URL / str(union.id)), follow_redirects=True)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not await is_instance_in_db(db_session, union)
