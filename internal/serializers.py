from typing import Any, Callable

import orjson
from pydantic import ConfigDict, BaseModel as PydanticBaseModel

__all__ = (
    'BaseModel',
)


def orjson_dumps(v: Any, *, default: Callable[[Any], Any] | None) -> str:
    """
    https://docs.pydantic.dev/1.10/usage/exporting_models/#custom-json-deserialisation
    """
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


class BaseModel(PydanticBaseModel):
    """
    Базовый класс для сериалайзеров Pydantic.
   """
    model_config = ConfigDict(
        str_strip_whitespace=True,
        str_min_length=1,
    )
