import datetime

from events.user_evetns import clear_user_cache, _background_tasks


async def test_clear_user_cache_func(user_in_redis_cache, users_cache):
    """
    Тест функции clear_user_cache которая чистит кеш юзера по сигналам удаления или изменения
    в таблице юзера.
    """
    assert await users_cache.exists_in_cache(user_in_redis_cache.id)

    task = clear_user_cache(None, None, user_in_redis_cache)
    assert task in _background_tasks

    await task

    assert task not in _background_tasks
    assert not await users_cache.exists_in_cache(user_in_redis_cache.id)


async def test_clear_user_cache_after_update(user_in_redis_cache, users_cache, db_session):
    """
    Сработает ли ф-ци clear_user_cache при апдейте юзера по сигналу.
    """
    assert await users_cache.exists_in_cache(user_in_redis_cache.id)

    user_in_redis_cache.updated_at = datetime.datetime.now(tz=datetime.UTC)
    await db_session.commit()

    assert not await users_cache.exists_in_cache(user_in_redis_cache.id)


async def test_clear_user_cache_after_delete(user_in_redis_cache, users_cache, db_session):
    """
    Сработает ли ф-ци clear_user_cache при удалении юзера по сигналу.
    """
    assert await users_cache.exists_in_cache(user_in_redis_cache.id)

    await db_session.delete(user_in_redis_cache)
    await db_session.commit()

    assert not await users_cache.exists_in_cache(user_in_redis_cache.id)