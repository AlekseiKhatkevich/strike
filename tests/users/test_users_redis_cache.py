import datetime

import pytest

from config import settings


async def test_delete_from_cache_by_id(users_cache, user_in_redis_cache, redis_conn):
    """
    Тест метода delete_from_cache_by_id который должен удалять юзера из кеша.
    """
    assert await redis_conn.hexists(users_cache.users_hash_name, user_in_redis_cache.id)

    await users_cache.delete_from_cache_by_id(user_in_redis_cache.id)

    assert not await redis_conn.hexists(users_cache.users_hash_name, user_in_redis_cache.id)


@pytest.mark.parametrize(
    'time_delta, should_update',
    [(datetime.timedelta(minutes=10), True), (datetime.timedelta(minutes=-10), False)]
)
def test_should_update_from_db(user_in_db, users_cache, time_delta, should_update):
    """
    Тест метода _should_update_from_db который определяет нужно ли обновлять кеш или нет.
    """
    now = datetime.datetime.now(tz=datetime.UTC)
    user_in_db._cached_at = now - (settings.user_cache_persistence + time_delta)

    assert users_cache._should_update_from_db(user_in_db) == should_update


async def test_add_user_into_redis(user_in_db, redis_conn, users_cache):
    """
    Тест метода _add_user_into_redis добавляющего юзера в кеш.
    """
    await users_cache._add_user_into_redis(user_in_db)

    assert await redis_conn.hexists(users_cache.users_hash_name, user_in_db.id)


async def test_get_user_from_redis(user_in_redis_cache, users_cache):
    """
    Тест метода get_user_from_redis получающего юзера из кеша редиса.
    """
    user_from_cache = await users_cache._get_user_from_redis(user_in_redis_cache.id)

    assert user_from_cache is not None


async def test_get_user_from_db(user_in_db, db_session, users_cache):
    """
    Тест метода get_user_from_db получающего юзера из БД.
    """
    user_from_db = await users_cache._get_user_from_db(db_session, user_in_db.id)

    assert user_from_db is user_in_db


async def test_get_user_user_in_redis(db_session, user_in_redis_cache, users_cache):
    """
    Тест метода get_user получающего юзера. Случай когда юзер есть в кеше.
    """
    user = await users_cache.get_user(db_session, user_in_redis_cache.id)

    assert user.id == user_in_redis_cache.id
    assert user in db_session


async def test_get_user_user_not_in_redis(db_session, user_in_db, redis_conn, users_cache):
    """
    Тест метода get_user получающего юзера. Случай когда юзера нет в кеше.
    """
    user = await users_cache.get_user(db_session, user_in_db.id)

    assert user.id == user_in_db.id
    assert user in db_session
    assert await redis_conn.hexists(users_cache.users_hash_name, user_in_db.id)
