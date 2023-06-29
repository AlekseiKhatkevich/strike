from fastapi import status
from yarl import URL

BASE_PATH = URL('/strikes/places/distance/')


async def test_distance_between_2_points(place,
                                         create_instance_from_factory,
                                         place_factory,
                                         async_client_httpx,
                                         ):
    """
    Позитивный тест эндпойнта '/distance/{id1}/{id2}/' отдающего дистанцию м/у 2мя точками.
    """
    place2 = await create_instance_from_factory(place_factory)
    url = BASE_PATH / str(place.id) / str(place2.id)

    response = await async_client_httpx.get(url.path, follow_redirects=True)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), float)
