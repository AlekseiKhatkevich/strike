import asyncio
from functools import wraps

from loguru import logger
from sqlalchemy import event

from internal.database import Base, async_session
from models import CRUDLog, CRUDTypes

__all__ = (
    'create_log',
)


async def _write_log_to_db(user_id, instance, action):
    #  нужна новая сессия так как основная ф-ция уже может закрыть свою сессию к этому моменту.
    session = async_session()
    try:
        session.add(CRUDLog(action=action, object=instance, user_id=user_id))
        await session.commit()
    except Exception as err:
        logger.exception(err)


async def _write_log_to_db_without_instance(user_id, ids, action, model):
    session = async_session()
    try:
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

    """
    @wraps(func)
    async def wrapper(session, *args, **kwargs):
        action = CRUDTypes.update
        known_model = None

        @event.listens_for(session.sync_session, 'pending_to_persistent')
        def _create(sess, instance):
            nonlocal action
            action = CRUDTypes.create

        @event.listens_for(session.sync_session, 'persistent_to_deleted')
        @event.listens_for(session.sync_session, 'deleted_to_detached')
        def _delete(sess, instance):
            nonlocal action
            action = CRUDTypes.delete

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

        user_id = session.info['current_user_id']
        if isinstance(res, Base):
            coro = _write_log_to_db(user_id, res, action)
        else:
            coro = _write_log_to_db_without_instance(user_id, res, action, known_model)

        asyncio.run_coroutine_threadsafe(coro, loop=asyncio.get_running_loop())

        return res

    return wrapper
