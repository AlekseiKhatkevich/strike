import pytest

from internal.dependencies import PBRequestData
from serializers.detentions import JailInSerializer
from serializers.proto.compiled import jail_pb2


@pytest.mark.parametrize('serializer', [None, JailInSerializer])
async def test_PBRequestData(fake_request, jail_inbound_pb, serializer):
    """
    Позитивный тест зависимости PBRequestData в случае с доп. сериалайзером и без него.
    """
    fake_request._body = jail_inbound_pb
    dependency = PBRequestData(jail_pb2.Jail, serializer=serializer)
    pb = jail_pb2.Jail()
    pb.ParseFromString(jail_inbound_pb)

    buff = await dependency(request=fake_request)

    assert buff.name == pb.name
    assert buff.address == pb.address
    assert buff.region_id == pb.region_id
