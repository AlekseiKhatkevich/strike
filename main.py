from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


# SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:1q2w3e@localhost:6432/tsdb"