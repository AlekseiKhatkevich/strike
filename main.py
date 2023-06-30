import os
from contextlib import asynccontextmanager
from typing import AsyncContextManager

from fastapi import FastAPI, status
from fastapi.responses import ORJSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import exc as sa_exc

from config import settings
from events import register_all_sqlalchemy_events
from internal.logging import configure_loggers
from internal.ratelimit import limiter
from models.exceptions import ModelEntryDoesNotExistsInDbError
from routers import users, token, places, union
from security.invitation import InvitationTokenDeclinedException

__all__ = (
    'app',
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncContextManager[None]:
    configure_loggers()
    app.state.limiter = limiter
    register_all_sqlalchemy_events()
    yield

app = FastAPI(
    default_response_class=ORJSONResponse,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(users.router, prefix='/users')
app.include_router(users.router_without_jwt, prefix='/users')
app.include_router(token.router, prefix='/token')
app.include_router(places.router, prefix='/strikes/places')
app.include_router(union.router, prefix='/strikes/unions')


@app.exception_handler(InvitationTokenDeclinedException)
async def invitation_token_exception_handler(_, exc: InvitationTokenDeclinedException) -> ORJSONResponse:
    """
    Обработчик исключения InvitationTokenDeclinedException.
    """
    return ORJSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={'detail': exc.text},
    )


@app.exception_handler(ModelEntryDoesNotExistsInDbError)
async def model_does_not_exists_exception_handler(_, exc: ModelEntryDoesNotExistsInDbError) -> ORJSONResponse:
    """
    Обработчик исключения ModelEntryDoesNotExistsInDbError.
    """
    return ORJSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': exc.text},
    )


@app.exception_handler(sa_exc.IntegrityError)
async def integrity_error_handler(_, exc: sa_exc.IntegrityError) -> ORJSONResponse:
    """
    Обработка IntegrityError из БД.
    https://www.postgresql.org/docs/current/errcodes-appendix.html
    """
    match exc.orig.pgcode:
        case '23505':
            exc_description = exc.orig.args[0].split(os.linesep)[-1]
            return ORJSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={'detail': f'Uniqueness violation {exc_description}'}
            )
        case _:
            raise exc
