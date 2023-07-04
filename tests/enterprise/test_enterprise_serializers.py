from serializers.enterprises import EnterpriseInSerializer, EnterpriseOutSerializer


def test_EnterpriseInSerializer_positive(enterprise_factory):
    """
    Позитивный тест сериалайзера EnterpriseInSerializer.
    """
    instance = enterprise_factory.build()
    EnterpriseInSerializer(
        name=instance.name,
        region_name=instance.region.name,
        place=instance.place,
        address=instance.address,
        field_of_activity=instance.field_of_activity,
    )


def test_EnterpriseOutSerializer_positive(enterprise_instance):
    """
    Позитивный тест сериалайзера EnterpriseOutSerializer.
    """
    EnterpriseOutSerializer.from_orm(enterprise_instance)
