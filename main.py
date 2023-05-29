from fastapi import FastAPI, status
from fastapi.responses import JSONResponse, ORJSONResponse
from fastapi.testclient import TestClient

from routers import users
from security.invitation import InvitationTokenDeclinedException

__all__ = (
    'app',
    'client',
)


app = FastAPI(default_response_class=ORJSONResponse)

app.include_router(users.router, prefix='/users')

client = TestClient(app)


@app.exception_handler(InvitationTokenDeclinedException)
async def invitation_toke_exception_handler(_, exc: InvitationTokenDeclinedException) -> JSONResponse:
    """

    """
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={'detail': exc.text},
    )


