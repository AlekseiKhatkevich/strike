import pytest
from sqlalchemy import delete, update

from crud.helpers import is_instance_in_db
from internal.dependencies import restrict_by_user_id
from models import Strike


@pytest.mark.parametrize('add_to_id, exists_in_db', [(0, True), (1, False)])
async def test_restrict_by_user_id_select(add_to_id,
                                          exists_in_db,
                                          db_session,
                                          user_in_db,
                                          strike,
                                          ):
    """
    Тест зависимости restrict_by_user_id. В случае селекта дожно быть добавлено
    ограничение в кверисет created_by_id == user_id, где user_id берется из JWT.
    Соответственно если он совпадает created_by_id записи в БД то мы ее получаем в
    результате селекта,  а если не совпадает - то не получаем.
    """
    gen = restrict_by_user_id(user_id=user_in_db.pk + add_to_id, session=db_session)

    next(gen)

    assert await is_instance_in_db(db_session, strike) == exists_in_db


@pytest.mark.parametrize('sql_action', [delete, update])
@pytest.mark.parametrize('add_to_id, has_happened', [(0, True), (1, False)])
async def test_restrict_by_user_id_delete(add_to_id,
                                          has_happened,
                                          sql_action,
                                          db_session,
                                          user_in_db,
                                          strike,
                                          ):
    """
    То же самое, что и для теста выше только случай для SQL DELETE и UPDATE.
    """

    gen = restrict_by_user_id(user_id=user_in_db.pk + add_to_id, session=db_session)

    next(gen)

    returned_ids = await db_session.scalar(
        sql_action(Strike).where(Strike.id == strike.id).returning(Strike.id)
    )

    assert (returned_ids == strike.id) == has_happened
