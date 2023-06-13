import datetime
import pickle
from typing import TYPE_CHECKING, Optional

import redis.asyncio as redis

from config import settings
from crud.users import get_user_by_id

if TYPE_CHECKING:
    from models import User
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = (
    'redis_connection',
    'UsersCache',
    'user_cache',
    'RedisConnectionContextManager',
)


redis_connection = redis.from_url(settings.redis_dsn)


class RedisConnectionContextManager:
    """
    Закрывает соединение по выходу, как и рекомендуют в документации.
    # https://redis.readthedocs.io/en/stable/examples/asyncio_examples.html
    """
    def __init__(self, connection: redis.Redis):
        self._connection = connection

    async def __aenter__(self) -> redis.Redis:
        return self._connection

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self._connection.close()


class UsersCache:
    """
    Кеш инстансов модели юзера.
    """
    users_hash_name = 'users_collection'

    def __init__(self, connection: redis.Redis = None, only_active: bool = False) -> None:
        self._connection = connection or redis_connection
        self.only_active = only_active

    async def delete_from_cache_by_id(self, user_id: int) -> None:
        """
        Удаляет запись кеша юзера по его id.
        """
        async with RedisConnectionContextManager(self._connection) as conn:
            await conn.hdel(self.users_hash_name, user_id)

    @staticmethod
    def _should_update_from_db(user: 'User') -> bool:
        """
        Нужно ли обновлять сохраненный инстанс юзера в редисе так как прошло уже много времени.
        """
        return datetime.datetime.now(tz=datetime.UTC) - user._cached_at > settings.user_cache_persistence

    async def get_user(self, session: 'AsyncSession', user_id: int) -> 'User':
        """
        Получает юзера либо из кеша, если он там есть либо из БД.
        """
        #  Пытаемся получить юзера из редиса
        user = await self._get_user_from_redis(user_id)
        if user is not None:  # если получили, то...
            if self._should_update_from_db(user):  # смотрим не просрочен ли срок его хранения в кеше
                return await self._get_user_from_db(session, user_id)  # если да - то обновляем из бд
            else:
                # если нет, то добавляем его в сессию (если нужно).
                return await session.merge(user, load=False) if user not in session else user
        else:  # если его нет в кеше - то получаем юзера из бд
            return await self._get_user_from_db(session, user_id)

    async def _add_user_into_redis(self, user: 'User') -> None:
        """
        Сохраняем инстанс юзера в редис.
        """
        # noinspection PyClassVar
        user._cached_at = datetime.datetime.now(tz=datetime.UTC)
        async with RedisConnectionContextManager(self._connection) as conn:
            await conn.hset(self.users_hash_name, user.id, pickle.dumps(user))

    async def _get_user_from_redis(self, user_id: int) -> Optional['User']:
        """
        Получаем данные юзера из редиса и десериализуем их до инстанса модели юзера.
        """
        async with RedisConnectionContextManager(self._connection) as conn:
            user_data = await conn.hget(self.users_hash_name, user_id)

        return pickle.loads(user_data) if user_data is not None else None

    async def _get_user_from_db(self, session: 'AsyncSession', user_id: int) -> 'User':
        """
        Получаем юзера из БД и сохраняем его в редис.
        """
        user = await get_user_by_id(session, user_id, raise_exc=True, only_active=self.only_active)
        await self._add_user_into_redis(user)
        return user


user_cache = UsersCache(only_active=True)
