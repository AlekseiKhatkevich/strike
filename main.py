from typing import Annotated

from fastapi import FastAPI, Depends

from config import Settings, get_settings

app = FastAPI()


@app.get("/")
async def root(settings: Annotated[Settings, Depends(get_settings)]):
    return settings.dict()


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

