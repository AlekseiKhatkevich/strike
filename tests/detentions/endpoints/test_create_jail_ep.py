from fastapi import status

from serializers.proto.compiled import jail_pb2

EP_URL = '/detentions/'


async def test_create_jail_ep_positive(db_session, async_client_httpx, jail_inbound_pb):
    """
    Позитивный тест эндпойнта POST /detentions/ создания крытой через протобаф.
    """
    data = jail_inbound_pb
    async_client_httpx.headers.update({'Content-Type': 'application/x-protobuf'})

    response = await async_client_httpx.post(EP_URL, content=data)

    assert response.status_code == status.HTTP_200_OK

    outbound_data = response.content
    pb = jail_pb2.Jail()
    pb.MergeFromString(outbound_data)

    assert pb.id is not None
    assert pb.name
    assert pb.address
    assert pb.region_id