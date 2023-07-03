from serializers.unions import UnionInSerializer, UnionOutSerializer


def test_UnionOutSerializer(union_factory):
    """
    Позитивный тест сериалайзера UnionOutSerializer.
    """
    union = union_factory.build(with_created_at=True, with_id=True)
    UnionOutSerializer.from_orm(union)


def test_UnionInSerializer(union_factory):
    """
    Позитивный тест сериалайзера UnionInSerializer.
    """
    union = union_factory.build(with_id=True)
    UnionInSerializer(**union.__dict__)
