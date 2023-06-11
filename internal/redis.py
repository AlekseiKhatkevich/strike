import pickle

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings

__all__ = (
    'redis_connection',
    'UsersCache',
)

from crud.users import get_user_by_id
from serializers.users import UserForRedisCacheSerializer

# https://redis.readthedocs.io/en/stable/examples/asyncio_examples.html

redis_connection = redis.from_url(settings.redis_dsn + '/1')


class UsersCache:
    """

    """
    users_hash_name = 'users_collection'

    def __init__(self, connection, only_active):
        self._connection = connection
        self.only_active = only_active

    async def get_user(self, session: AsyncSession, user_id):
        user = await self._get_user_from_redis(user_id)
        if user is not None:
            return await session.merge(user, load=False)
        else:
            user = await self._get_user_from_db(session, user_id)
            await self._add_user_into_redis(user)
            return user

    async def _add_user_into_redis(self, user):
        await self._connection.hset(self.users_hash_name, user.id, pickle.dumps(user))
        await self._connection.close()

    async def _get_user_from_redis(self, user_id):
        user_data = await self._connection.hget(self.users_hash_name, user_id)
        await self._connection.close()
        if user_data is None:
            return None
        user = pickle.loads(user_data)
        return user

    async def _get_user_from_db(self, session, user_id):
        return await get_user_by_id(session, user_id, raise_exc=True, only_active=self.only_active)
