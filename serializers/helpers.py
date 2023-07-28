from typing import Annotated

from pydantic import AfterValidator, AwareDatetime, PlainSerializer, WithJsonSchema
from sqlalchemy.dialects.postgresql import Range

__all__ = (
    'RangeField',
)


def range_validator(value: list[AwareDatetime | None]) -> list[AwareDatetime | None]:
    """
    Валидация входящих данных для поля duration.
    """
    dt1, dt2 = value
    if dt1 and dt2 and dt1 >= dt2:
        raise ValueError('Second datetime in range should be greater then first one.')
    elif not dt1 and not dt2:
        raise ValueError('Please specify at leas one datetime in range.')
    return value


RangeField = Annotated[
    list[AwareDatetime | None],
    AfterValidator(range_validator),
    PlainSerializer(lambda x: Range(*x), when_used='json'),
    WithJsonSchema({'type': 'dict'}, mode='serialization'),
]
