import asyncio
from functools import wraps

from loguru import logger
from sqlalchemy import event

from models import CRUDLog, CRUDTypes

__all__ = (
    'create_log',
)


async def _write_log_to_db(session, instance, action):
    try:
        user_id = session.info['current_user_id']
        session.add(CRUDLog(action=action, object=instance, user_id=user_id))
        await session.commit()
    except Exception as err:
        logger.exception(err)


def create_log(func):
    """
    https://stackoverflow.com/questions/64497615/how-to-add-a-custom-decorator-to-a-fastapi-route
    """

    @wraps(func)
    async def wrapper(session, *args, **kwargs):
        action = CRUDTypes.update

        @event.listens_for(session.sync_session, "pending_to_persistent")
        def _save(sess, instance):
            nonlocal action
            action = CRUDTypes.create

        res = await func(session, *args, **kwargs)
        asyncio.run_coroutine_threadsafe(
            _write_log_to_db(session, res, action),
            loop=asyncio.get_running_loop(),
        )

        return res

    return wrapper
