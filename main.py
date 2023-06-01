from fastapi import FastAPI, status
from fastapi.responses import ORJSONResponse

from routers import users
from security.invitation import InvitationTokenDeclinedException

__all__ = (
    'app',
)


app = FastAPI(default_response_class=ORJSONResponse)

app.include_router(users.router, prefix='/users')


@app.exception_handler(InvitationTokenDeclinedException)
async def invitation_token_exception_handler(_, exc: InvitationTokenDeclinedException) -> ORJSONResponse:
    """

    """
    return ORJSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={'detail': exc.text},
    )


