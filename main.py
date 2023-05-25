from typing import Annotated

from fastapi import FastAPI, Depends

from config import Settings, get_settings

# meta = MetaData()
# engine = create_async_engine(
#         settings.pg_dsn,
#         echo=True,
#         echo_pool=True,
#     )



app = FastAPI()


@app.get("/")
async def root(settings: Annotated[Settings, Depends(get_settings)]):
    pass


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

