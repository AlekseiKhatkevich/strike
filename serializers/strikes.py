import datetime
from typing import Annotated
from sqlalchemy.dialects.postgresql.ranges import Range
from pydantic import Field

from internal.serializers import BaseModel


__all__ = (
    'StrikeInSerializer',
)


class DatetimeRangeField(Range[datetime.datetime | None]):
    """

    """
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, _range):
        for dt in _range:
            if not isinstance(dt, (datetime.datetime, type(None))):
                raise ValueError('Only datetime objects are accepted')
            elif dt is not None and dt.tzinfo is None:
                raise ValueError('Only aware datetime are accepted')

        dt1, dt2 = _range
        if dt1 and dt2 and dt1 >= dt2:
            raise ValueError('Second datetime in range should be greater then first one.')
        elif not dt1 and not dt2:
            raise ValueError('Please specify at leas one datetime in range.')

        return cls(*_range)


class StrikeInSerializer(BaseModel):
    """

    """
    duration: DatetimeRangeField | None
