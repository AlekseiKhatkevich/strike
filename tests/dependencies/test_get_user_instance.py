from internal.dependencies import get_user_instance


async def test_get_user_instance(user_in_db, db_session):
    """
    Тест зависимости get_user_instance которая возвращает юзера.
    """
    user = await get_user_instance(db_session, user_in_db.id)

    assert user is user_in_db
