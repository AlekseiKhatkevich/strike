from typing_and_types import Annotated

from fastapi import FastAPI, Depends

from config import Settings, get_settings


app = FastAPI()


@app.get("/")
async def root(settings: Annotated[Settings, Depends(get_settings)]):
    pass


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

