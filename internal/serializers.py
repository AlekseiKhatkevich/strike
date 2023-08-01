from typing import Any, Callable

import orjson
from pydantic import BaseModel as PydanticBaseModel, ConfigDict
from pydantic._internal import _annotated_handlers
from pydantic.types import _check_annotated_type
from pydantic_core import core_schema

__all__ = (
    'BaseModel',
    'PastAwareDatetime',
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


class PastAwareDatetime:
    """
    Объект datetime с временной зоной в прошлом.
    """
    @classmethod
    def __get_pydantic_core_schema__(
            cls, source: type[Any], handler: _annotated_handlers.GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        if cls is source:
            # used directly as a type
            return core_schema.datetime_schema(now_op='past', tz_constraint='aware')
        else:
            schema = handler(source)
            _check_annotated_type(schema['type'], 'datetime', cls.__name__)
            schema['now_op'] = 'past'
            schema['tz_constraint'] = 'aware'
            return schema

    def __repr__(self) -> str:
        return 'PastAwareDatetime'
