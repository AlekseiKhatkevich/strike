from contextlib import asynccontextmanager
from typing import AsyncContextManager

from fastapi import FastAPI, status
from fastapi.responses import ORJSONResponse

from config import settings
from internal.logging import configure_loggers
from routers import users
from security.invitation import InvitationTokenDeclinedException

__all__ = (
    'app',
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncContextManager[None]:
    configure_loggers()
    yield

app = FastAPI(
    default_response_class=ORJSONResponse,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(users.router, prefix='/users')


@app.exception_handler(InvitationTokenDeclinedException)
async def invitation_token_exception_handler(_, exc: InvitationTokenDeclinedException) -> ORJSONResponse:
    """
    Обработчик исключения InvitationTokenDeclinedException.
    """
    return ORJSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={'detail': exc.text},
    )
