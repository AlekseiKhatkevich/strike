from functools import reduce

from fastapi import status
from sqlalchemy.sql import column

from crud.helpers import exists_in_db
from models import Enterprise

EP_URL = '/strikes/enterprises/'


async def test_create_or_update_enterprise_ep_create(db_session,
                                                     async_client_httpx,
                                                     enterprise_factory,
                                                     region,
                                                     ):
    """
    Позитивный тест эндпойнта POST '/strikes/enterprises/' создание Enterprise.
    """
    instance = enterprise_factory.build(region=region)
    data = dict(
        name=instance.name,
        region_name=instance.region.name,
        place=instance.place,
        address=instance.address,
        field_of_activity=instance.field_of_activity,
    )

    response = await async_client_httpx.post(EP_URL, json=data)
    assert response.status_code == status.HTTP_201_CREATED
    assert await exists_in_db(
        db_session,
        Enterprise,
        reduce(lambda x, y: x & y, (column(x) == y for x, y in data.items())),
    )


async def test_create_or_update_enterprise_ep_update(db_session,
                                                     async_client_httpx,
                                                     enterprise_instance,
                                                     ):
    """
    Позитивный тест эндпойнта PUT '/strikes/enterprises/' обновление Enterprise.
    """
    new_name = 'new_name'
    new_addr = 'Ул. 8 марта дом. 8'
    data = dict(
        id=enterprise_instance.id,
        name=new_name,
        region_name=enterprise_instance.region_name,
        place=enterprise_instance.place,
        address=new_addr,
    )

    response = await async_client_httpx.put(EP_URL, json=data)
    assert response.status_code == status.HTTP_200_OK
    assert await exists_in_db(
        db_session,
        Enterprise,
        reduce(lambda x, y: x & y, (column(x) == y for x, y in data.items())),
    )
