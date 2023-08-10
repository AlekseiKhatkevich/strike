query = """
    query Detentions {
    detentions %s {
        id
        duration
        name
        extraPersonalInfo
        needsMedicalAttention
        needsLawyer
        jailId
        charge
        transferredFromId
        relativeOrFriend
        jail {
            id
            name
            address
            regionId
        }
            }
        }  
    """


async def test_detentions_q(detention, schema_f):
    """
    Позитивный тест квери detentions.
    """
    response = await schema_f(query % '')

    assert response.errors is None
    detentions = response.data['detentions']
    assert len(detentions) == 1
    assert detentions[0]['id'] == detention.id
    assert detentions[0]['jail']['id'] == detention.jail_id


async def test_detentions_q_filter_by_name(detention_factory, db_session, schema_f):
    """
    Позитивный тест квери detentions. Случай с фильтрацией по полю name.
    """

    detention1, detention2 = detention_factory.build_batch(size=2)
    db_session.add_all([detention1, detention2])
    await db_session.commit()

    response = await schema_f(query % f'(name: "{detention1.name}")')
    assert response.errors is None
    detentions = response.data['detentions']
    assert len(detentions) == 1
    assert detentions[0]['id'] == detention1.id
