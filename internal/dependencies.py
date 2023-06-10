from typing import Annotated, AsyncGenerator

import jwt
from fastapi import Depends, status, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings, Settings
from internal.database import async_session, db_session_context_var
from security import sensitive
from security.jwt import validate_jwt_token

__all__ = (
    'SessionDep',
    'SettingsDep',
    'UserIdDep',
    'jwt_authorize',
    'get_session',
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


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
        return user_id


SessionDep = Annotated[AsyncSession, Depends(get_session, use_cache=False)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
UserIdDep = Annotated[int, Depends(jwt_authorize)]
