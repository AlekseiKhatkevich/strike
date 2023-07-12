import pytest
from fastapi import HTTPException
from fastapi_pagination import Params
from sqlalchemy import exc as sa_exc
from sqlalchemy.dialects.postgresql import insert

from crud.helpers import (
    create_or_update_with_session_get,
    delete_via_sql_delete,
    exists_in_db,
    flush_and_raise,
    get_collection_paginated,
    get_constr_name_from_integrity_error, get_id_from_integrity_error,
    get_text_from_integrity_error,
)
from models import Region, Union, User
from models.exceptions import ModelEntryDoesNotExistsInDbError


@pytest.fixture
def params() -> Params:
    """
    Для пагинации.
    """
    return Params(page=1, size=100)


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
    expected_error_message = f'{Union.__name__} with id=99999999999 was not found in DB.'

    with pytest.raises(ModelEntryDoesNotExistsInDbError, match=expected_error_message):
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


async def test_get_collection_paginated_all_positive(db_session, unions_batch, params):
    """
    Позитивный тест ф-ции get_collection_paginated. Возвращает все имеющиеся записи.
    """
    res = await get_collection_paginated(db_session, Union, [], params)

    assert len(res.items) == 10


async def test_get_collection_paginated_by_id(db_session, unions_batch, params):
    """
    Позитивный тест ф-ции get_collection_paginated. Возвращает лишь записи по их id.
    """
    ids = {unions_batch[0].id, unions_batch[-1].id}
    res = await get_collection_paginated(db_session, 'Union', ids, params)

    assert len(res.items) == 2
    assert {entry.id for entry in res.items} == ids


async def test_get_collection_paginated_with_pagination(db_session, unions_batch):
    """
    Позитивный тест ф-ции get_collection_paginated. Пагинация при size=5 должна отдать только 5 записей
    из 10ти.
    """
    res = await get_collection_paginated(db_session, Union, [], Params(page=1, size=5))

    assert len(res.items) == 5


async def test_get_text_from_integrity_error(region, db_session):
    """
    Позитивный тест ф-ции get_text_from_integrity_error которая получает текст
    сообщения об ошибке оригинальный выработанный в БД из IntegrityError.
    """
    try:
        await db_session.execute(insert(Region).values(
            {'name': region.name, 'contour': region.contour}
        ))
    except sa_exc.IntegrityError as err:
        error_text = get_text_from_integrity_error(err)

        assert error_text == f'DETAIL:  Ключ "(name)=({region.name})" уже существует.'


async def test_get_id_from_integrity_error(region, db_session):
    """
    Позитивный тест ф-ции get_id_from_integrity_error которая получает id
    инстанса из IntegrityError.
    """
    try:
        await db_session.execute(insert(Region).values(
            {'name': region.name, 'contour': region.contour}
        ))
    except sa_exc.IntegrityError as err:
        _id = get_id_from_integrity_error(err)

        assert _id == region.name


async def test_get_constr_name_from_integrity_error(strike_factory, create_instance_from_factory):
    """
    Позитивный тест ф-ции get_constr_name_from_integrity_error для получения названия
    check constraint из текста сообщения из IntegrityError.
    """
    with pytest.raises(sa_exc.IntegrityError) as err:
        # noinspection PyCallingNonCallable
        await create_instance_from_factory(
            strike_factory,
            duration=None,
        )

        assert get_constr_name_from_integrity_error(err) == 'ck_strikes_one_of_dates_is_not_null'


async def test_flush_and_reraise(region, db_session):
    """
    Позитивный тест ф-ции flush_and_raise которая перехватывает IntegrityError и рейзит
    HTTPException после попытки сделать flush() в БД.
    """
    db_session.expunge_all()
    db_session.add(Region(name=region.name, contour=region.contour))
    error_message = 'test {id}'

    with pytest.raises(HTTPException) as err:
        await flush_and_raise(db_session, error_message)

        assert err.detail == error_message.format(region.id)
