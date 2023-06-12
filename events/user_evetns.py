import asyncio

from sqlalchemy.event import listen

from internal.redis import user_cache
from models import User

__all__ = (
    'clear_user_cache',
)

_background_tasks = set()


def clear_user_cache(mapper, connection, target):
    """
    Очищает кеш юзера при его обновлении или удалении.
    """
    task = asyncio.create_task(user_cache.delete_from_cache_by_id(target.id))
    # https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task (weak refs!!!)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)


def register():
    listen(User, 'after_update', clear_user_cache)
    listen(User, 'after_delete', clear_user_cache)
