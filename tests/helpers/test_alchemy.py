import pytest

from crud.helpers import create_or_update_with_session_get, delete_via_sql_delete, exists_in_db
from models import Union, User


async def test_exists_in_db_positive(db_session, user_in_db):
    """
    Позитивный тест ф-ции exists_in_db.
    """
    assert await exists_in_db(db_session, User, User.id == user_in_db.id)


@pytest.mark.no_db_calls
async def test_exists_in_db_negative(db_session):
    """
    Негативный тест ф-ции exists_in_db.
    """
    assert not await exists_in_db(db_session, User, User.id == 99999999999)


@pytest.mark.parametrize('model', [Union, 'Union'])
async def test_create_or_update_with_session_get_create_positive(model, db_session, faker):
    """
    Позитивный тест ф-ции create_or_update_with_session_get.
    Должна создавать запись в БД если не передан id. Можно передавать модель как
    класс или как строку.
    """
    data = {'name': faker.company()}

    saved_union = await create_or_update_with_session_get(db_session, model, data)

    assert await exists_in_db(db_session, Union, Union.id == saved_union.id)


async def test_create_or_update_with_session_get_update_positive(union, db_session, faker):
    """
    Позитивный тест ф-ции create_or_update_with_session_get. Должна обновлять запись
    если передан id.
    """
    new_name = faker.company()
    data = {'name': new_name, 'id': union.id}

    saved_union = await create_or_update_with_session_get(db_session, type(union), data)

    assert await exists_in_db(
        db_session,
        Union,
        (Union.id == saved_union.id) & (Union.name == new_name),
    )


async def test_create_or_update_with_session_get_update_negative(union, db_session, faker):
    """
    Негативный тест ф-ции create_or_update_with_session_get. Если при обновлении передан
    id которого нет в БД - возбуждаем исключение.
    """
    data = {'name': faker.company(), 'id': 99999999999}
    expected_error_message = f'{Union} with id=99999999999 was not found in DB.'

    with pytest.raises(ValueError, match=expected_error_message):
        await create_or_update_with_session_get(db_session, type(union), data)


async def test_delete_via_sql_delete_positive(unions_batch, db_session):
    """
    Позитивный тест метода delete_via_sql_delete удаления чего либо из БД.
    """
    ids_to_delete = unions_batch[0].id, unions_batch[-1].id
    await delete_via_sql_delete(
        db_session,
        Union,
        Union.id.in_(ids_to_delete),
    )
    assert not await exists_in_db(db_session, Union, Union.id.in_(ids_to_delete))