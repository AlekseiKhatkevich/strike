from internal.protobuf import pb_from_model_instance
from serializers.proto.compiled import jail_pb2


def test_pb_from_model_instance_positive(jail):
    """
    Позитивный тест ф-ции pb_from_model_instance заполняющей буфер атрибутами экземпляра
    класса модели.
    """
    pb = jail_pb2.Jail

    pb = pb_from_model_instance(pb, jail)

    assert pb.IsInitialized()

    assert pb.id == jail.id
    assert pb.name == jail.name
    assert pb.region_id == jail.region_id
    assert pb.address == jail.address
