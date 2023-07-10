import contextvars
from typing import Annotated, AsyncGenerator, TYPE_CHECKING

import jwt
from fastapi import Depends, HTTPException, Path, Request, status
from fastapi.params import Query
from fastapi.security import OAuth2PasswordBearer
from fastapi_pagination import Params
from fastapi_pagination.bases import AbstractParams
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings, get_settings
from internal.database import async_session, db_session_context_var
from internal.redis import user_cache
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


def jwt_authorize(jwt_token: Annotated[str, Depends(oauth2_scheme)], request: Request) -> int:
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
        return user_id


SessionNonCachedDep = Annotated[AsyncSession, Depends(get_session, use_cache=False)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
UserIdDep = Annotated[int, Depends(jwt_authorize)]
PaginParamsDep = Annotated[AbstractParams, Depends(Params)]


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
