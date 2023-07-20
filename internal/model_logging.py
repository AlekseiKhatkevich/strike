import asyncio
from functools import wraps

from loguru import logger
from sqlalchemy import event

from internal.database import Base
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


async def _write_log_to_db_without_instance(session, ids, action, model):
    try:
        user_id = session.info['current_user_id']
        log_entries = [
            CRUDLog(action=action, object_id=_id, user_id=user_id, object_type=model.__name__)
            for _id in ids
        ]
        session.add_all(log_entries)
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
        known_model = None

        @event.listens_for(session.sync_session, 'pending_to_persistent')
        def _save(sess, instance):
            nonlocal action
            action = CRUDTypes.create

        @event.listens_for(session.sync_session, 'do_orm_execute')
        def receive_do_orm_execute(orm_execute_state):
            nonlocal action, known_model
            if orm_execute_state.is_delete:
                action = CRUDTypes.delete
                known_model = orm_execute_state.bind_mapper.entity
            elif orm_execute_state.is_update:
                action = CRUDTypes.update
                known_model = orm_execute_state.bind_mapper.entity

        res = await func(session, *args, **kwargs)

        if isinstance(res, Base):
            coro = _write_log_to_db(session, res, action)
        else:
            coro = _write_log_to_db_without_instance(session, res, action, known_model)

        asyncio.run_coroutine_threadsafe(coro, loop=asyncio.get_running_loop())

        return res

    return wrapper
