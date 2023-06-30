from serializers.unions import UnionOutSerializer


def test_UnionOutSerializer(union_factory):
    """
    Позитивный тест сериалайзера UnionOutSerializer.
    """
    union = union_factory.build(with_created_at=True, with_id=True)
    UnionOutSerializer.from_orm(union)
