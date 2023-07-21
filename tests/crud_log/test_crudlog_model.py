from models import CRUDLog, CRUDTypes, Union


async def test_CRUDLog_model_positive(db_session, faker, user_in_db):
    """
    Позитивный тест создания инстанса модели CRUDLog и сохранения его в БД.
    """
    instance = CRUDLog(
        object_type=Union.__name__,
        object_id=faker.pyint(min_value=1),
        action=faker.random_element(elements=list(CRUDTypes)),
        user_id=user_in_db.id,
    )
    db_session.add(instance)
    await db_session.commit()

    assert instance.id is not None
