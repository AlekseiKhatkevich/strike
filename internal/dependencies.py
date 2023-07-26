import asyncio
import contextvars
import datetime
from typing import Annotated, Any, AsyncGenerator, Iterator, TYPE_CHECKING

import jwt
from fastapi import Depends, HTTPException, Path, Request, status
from fastapi.params import Query
from fastapi.security import OAuth2PasswordBearer
from fastapi_pagination import Params
from fastapi_pagination.bases import AbstractParams
from loguru import logger
from sqlalchemy import event
from sqlalchemy.dialects.postgresql import Range
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import ORMExecuteState, with_loader_criteria

from config import Settings, get_settings
from internal.database import async_session, db_session_context_var
from internal.model_logging import _write_log_to_db
from internal.redis import user_cache
from models import CRUDTypes, Strike
from security import sensitive
from security.jwt import validate_jwt_token

if TYPE_CHECKING:
    from models.users import User

__all__ = (
    'SessionDep',
    'SettingsDep',
    'UserIdDep',
    'UserModelInstDep',
    'jwt_authorize',
    'get_session',
    'get_user_instance',
    'PaginParamsDep',
    'PathIdDep',
    'GetParamsIdsDep',
    'user_id_context_var',
    'LogDep',
    'log',
    'RestrictByUserIdDep',
    'restrict_by_user_id',
    'DtRangeDep',
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
user_id_context_var: contextvars.ContextVar[int] = contextvars.ContextVar('user_id')


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Асинхронная сессия БД.
    """
    async with async_session() as _session:
        #  получить сессию через s = db_session_context_var.get()
        db_session_context_var.set(_session)
        yield _session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


def jwt_authorize(session: SessionDep,
                  jwt_token: Annotated[str, Depends(oauth2_scheme)],
                  request: Request,
                  ) -> int:
    """
    Достает JWT токен из хедера запроса, валидирует его возвращая user_id в случае успеха.
    """
    try:
        user_id = validate_jwt_token(jwt_token.strip())
    except jwt.PyJWTError as err:
        logger.info(f'Token {sensitive(jwt_token)} was rejected. Exception - {err}')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        ) from err
    else:
        request.state.user_id = user_id
        user_id_context_var.set(user_id)
        session.info['current_user_id'] = user_id
        return user_id


SessionNonCachedDep = Annotated[AsyncSession, Depends(get_session, use_cache=False)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
UserIdDep = Annotated[int, Depends(jwt_authorize)]
PaginParamsDep = Annotated[AbstractParams, Depends(Params)]


async def log(user_id: UserIdDep, session: SessionDep) -> None:
    """
    Запись лога объекта в БД.
    """
    action = None
    known_instance = None
    known_model = None
    known_persistent_classes = set()

    def _after_update(mapper, connection, target):
        nonlocal action, known_instance
        action = CRUDTypes.update
        known_instance = target

    @event.listens_for(session.sync_session, 'pending_to_persistent')
    def _create(sess, instance):
        """Эвент создания записи модели через сессию."""
        nonlocal action, known_instance
        action = CRUDTypes.create
        known_instance = instance

    @event.listens_for(session.sync_session, 'loaded_as_persistent')
    def receive_loaded_as_persistent(session, instance):
        """
        Регистрируем эвент для каждого загружаемого класса из БД на случай возможного
        апдейта одного из его инстансов.
        """
        cls = instance.__class__
        if cls not in known_persistent_classes:
            known_persistent_classes.add(cls)
            event.listen(cls, 'after_update', _after_update)

    @event.listens_for(session.sync_session, 'persistent_to_deleted')
    @event.listens_for(session.sync_session, 'deleted_to_detached')
    def _delete(sess, instance):
        """Эвенты удаления записи модели через сессию. 2 разных так как может быть rollback."""
        nonlocal action, known_instance
        known_instance = instance
        action = CRUDTypes.delete

    @event.listens_for(session.sync_session, 'do_orm_execute')
    def receive_do_orm_execute(orm_execute_state):
        """Эвент обновления или удаления записей ч/з SQL update / delete."""
        nonlocal action, known_model
        if orm_execute_state.is_delete:
            known_model = orm_execute_state.bind_mapper.entity
            action = CRUDTypes.delete
        elif orm_execute_state.is_update:
            known_model = orm_execute_state.bind_mapper.entity
            action = CRUDTypes.update

    yield None

    if user_id is not None and action is not None:
        coro = _write_log_to_db(known_instance, user_id, action, known_model)
        asyncio.run_coroutine_threadsafe(coro, loop=asyncio.get_running_loop())


LogDep = Annotated[Any, Depends(log)]


async def get_user_instance(session: SessionDep, user_id: UserIdDep) -> 'User':
    """
    Отдает инстанс модели юзера.
    """
    user = await user_cache.get_user(session, user_id)
    session.info['current_user'] = user
    return user


UserModelInstDep = Annotated['User', Depends(get_user_instance)]


def id_in_path(_id: int = Path(ge=1, alias='id')) -> int:
    """
    Получение id из урла.
    """
    return _id


PathIdDep = Annotated[int, Depends(id_in_path)]


def id_list_in_query_params(_id: list[int] = Query([], alias='id')):
    """
    Получение набора id из гет-параметров урла.
    """
    return _id


GetParamsIdsDep = Annotated[list[int], Depends(id_list_in_query_params)]


def restrict_by_user_id(user_id: UserIdDep, session: SessionDep) -> Iterator[None]:
    """
    Ограничивает кверисет только теми страйками который создал реквест юзер.
    """
    @event.listens_for(session.sync_session, 'do_orm_execute')
    def _add_filtering_criteria(execute_state: ORMExecuteState) -> None:
        if (
                execute_state.is_select
                or execute_state.is_delete
                or execute_state.is_update
                and not execute_state.is_column_load
                and not execute_state.is_relationship_load
        ):
            execute_state.statement = execute_state.statement.options(
                with_loader_criteria(
                    Strike,
                    Strike.created_by_id == user_id,
                    include_aliases=True,
                )
            )
            session.info['qs_restricted_by_user_id'] = user_id

    yield None
    del session.info['qs_restricted_by_user_id']


RestrictByUserIdDep = Annotated[Any, Depends(restrict_by_user_id)]


def dt_range_query_param(
        dt_from: datetime.datetime | None = None,
        dt_to: datetime.datetime | None = None,
) -> Range[datetime.datetime]:
    """
    """
    if dt_from is None and dt_to is None:
        dt_from = datetime.datetime.min.replace(tzinfo=datetime.UTC)
        dt_to = datetime.datetime.max.replace(tzinfo=datetime.UTC)

    return Range(dt_from, dt_to)


DtRangeDep = Annotated[Range[datetime.datetime], Depends(dt_range_query_param)]
