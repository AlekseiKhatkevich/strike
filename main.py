from fastapi import FastAPI

from routers import users

__all__ = (
    'app',
)

app = FastAPI()
app.include_router(users.router)
