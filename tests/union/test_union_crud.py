from fastapi_pagination import Params

from crud.unions import get_unions

params = Params(page=1, size=100)


async def test_get_unions(db_session, unions_batch):
    """
    Позитивный тест ф-ции get_unions. Возвращает все имеющиеся записи Union.
    """
    res = await get_unions(db_session, [], params)

    assert len(res.items) == 10


async def test_get_unions_by_id(db_session, unions_batch):
    """
    Позитивный тест ф-ции get_unions. Возвращает некоторые записи по их id.
    """
    ids = {unions_batch[0].id, unions_batch[-1].id}
    res = await get_unions(db_session, ids, params)

    assert len(res.items) == 2
    assert {entry.id for entry in res.items} == ids


async def test_get_unions_with_pagination(db_session, unions_batch):
    """
    Позитивный тест ф-ции get_unions. Пагинация при size=5 должна отдать только 5 записей
    из 10ти.
    """
    res = await get_unions(db_session, [], Params(page=1, size=5))

    assert len(res.items) == 5
