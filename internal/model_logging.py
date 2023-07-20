import asyncio
from functools import singledispatch, wraps
from typing import Callable, TYPE_CHECKING, Type

from loguru import logger
from sqlalchemy import event

from internal.database import Base, async_session
from models import CRUDLog, CRUDTypes

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = (
    'create_log',
)


async def _write_log_to_db(result: Base | list[int, ...],
                           user_id: int,
                           action: CRUDTypes,
                           model: Type[Base] | None = None,
                           ) -> None:
    """
    Создает запись лога в БД.

    :param result: Результат работы CRUD ф-ции. Либо инстанс модели, обычно в случае создания или
    удаления записи либо список id объектов (обычно в случае удаления).
    :param user_id: Первичный ключ юзера совершившего действие.
    :param action: Тип действия.
    :param model: Модель (класс) над инстансом которой было проведено действие.
    :return: None
    """
    with async_session() as session:
        try:
            _branch_log_creation(result, session, user_id, action, model)
            await session.commit()
        except Exception as err:
            logger.exception(err)


@singledispatch
def _branch_log_creation(result,
                         session: 'AsyncSession',
                         user_id: list[int, ...],
                         action: CRUDTypes,
                         model: Type[Base],
                         *args, **kwargs,
                         ) -> None:
    """
    Создает записи лога в сессии. Случай когда результатом ф-ции является список id объектов.
    """
    log_entries = [
        CRUDLog(action=action, object_id=_id, user_id=user_id, object_type=model.__name__)
        for _id in result
    ]
    session.add_all(log_entries)


@_branch_log_creation.register
def _(result: Base, session, user_id, action, *args, **kwargs):
    """
    Создает записи лога в сессии. Случай когда результатом ф-ции является инстанс модели.
    """
    session.add(CRUDLog(action=action, object=result, user_id=user_id))


def create_log(func: Callable) -> Callable:
    """
    Декоратор для вьюх энпойнтов фастапи создающий записи в логе CRUDLog о совершенных
    действиях.
    """
    @wraps(func)
    async def wrapper(session: 'AsyncSession', *args, **kwargs):
        action = CRUDTypes.update
        known_model = None

        @event.listens_for(session.sync_session, 'pending_to_persistent')
        def _create(sess, instance):
            """Эвент создания записи модели через сессию."""
            nonlocal action
            action = CRUDTypes.create

        @event.listens_for(session.sync_session, 'persistent_to_deleted')
        @event.listens_for(session.sync_session, 'deleted_to_detached')
        def _delete(sess, instance):
            """Эвенты удаления записи модели через сессию. 2 разных так как может быть rollback."""
            nonlocal action
            action = CRUDTypes.delete

        @event.listens_for(session.sync_session, 'do_orm_execute')
        def receive_do_orm_execute(orm_execute_state):
            """Эвент обновления или удаления записей ч/з SQL update / delete."""
            nonlocal action, known_model
            known_model = orm_execute_state.bind_mapper.entity
            if orm_execute_state.is_delete:
                action = CRUDTypes.delete
            elif orm_execute_state.is_update:
                action = CRUDTypes.update

        result: Base | list[int, ...] = await func(session, *args, **kwargs)

        user_id = session.info['current_user_id']
        # запускаем создание лога без ожидания аля fire-and-forget.
        coro = _write_log_to_db(result, user_id, action, known_model)
        asyncio.run_coroutine_threadsafe(coro, loop=asyncio.get_running_loop())

        return result

    return wrapper
