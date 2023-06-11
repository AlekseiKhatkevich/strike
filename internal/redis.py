from contextlib import asynccontextmanager
from functools import partial
import redis.asyncio as redis
from config import settings

__all__ = (
    'redis_connection',
    'UsersCache',
)

from crud.users import get_user_by_id
from models import User
from serializers.users import UserForRedisCacheSerializer

# https://redis.readthedocs.io/en/stable/examples/asyncio_examples.html

redis_connection = redis.from_url(settings.redis_dsn + '/1')


class UsersCache:
    """

    """
    users_hash_name = 'users_collection'
    serializer = UserForRedisCacheSerializer

    def __init__(self, connection, only_active):
        self._connection = connection
        self.only_active = only_active

    async def get_user(self, session, user_id):
        user = await self._get_user_from_redis(user_id)

    async def _get_user_from_redis(self, user_id):
        async with self._connection as conn:
            user_json_b = await conn.hget(self.users_hash_name, user_id)
        if user_json_b is None:
            return None
        user_ser = self.serializer.parse_raw(user_json_b)
        return User(**user_ser.dict())

    async def _get_user_from_db(self, session, user_id):
        return await get_user_by_id(session, user_id, raise_exc=True, only_active=self.only_active)

