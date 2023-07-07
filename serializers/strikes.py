import datetime
from typing import Annotated, ClassVar

from pydantic import Field, PrivateAttr, validator
from pydantic.datetime_parse import StrBytesIntFloat, parse_datetime
from sqlalchemy.dialects.postgresql.ranges import Range

from internal.serializers import BaseModel
from models import UserRole
from serializers.enterprises import EnterpriseInSerializer
from serializers.places import PlaceInSerializer

__all__ = (
    'StrikeInSerializer',
)

from serializers.typing import IntIdType


class DatetimeRangeField(Range[datetime.datetime | None]):
    """

    """
    @staticmethod
    def _parse_datetime_range(
            raw_range: list[datetime.datetime | StrBytesIntFloat | None, ...],
    ) -> list[datetime.datetime | None, ...]:
        """

        """
        dt_range = []
        for dt in raw_range:
            if dt is None:
                dt_range.append(dt)
            else:
                dt_range.append(parse_datetime(dt))
        return dt_range

    @classmethod
    def __get_validators__(cls):
        yield cls._parse_datetime_range
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


class UsersInvolvedInSerializer(BaseModel):
    """

    """
    user_id: IntIdType
    role: UserRole

    @validator('role', pre=True)
    def _role_upper(cls, role: str, values, **kwargs) -> str:
        return role.upper()


class StrikeInSerializer(BaseModel):
    """

    """
    duration: DatetimeRangeField | None
    planned_on_date: datetime.date | None
    goals: str
    results: str | None
    overall_num_of_employees_involved: IntIdType
    enterprise: IntIdType | EnterpriseInSerializer
    union_in_charge_id: IntIdType | None
    group: list[IntIdType] | None
    places: list[IntIdType | PlaceInSerializer] | None
    users_involved: list[UsersInvolvedInSerializer] | None
    _created_by_id = PrivateAttr()

    @validator('planned_on_date', always=True)
    def _validate_duration_or_planned_on_date_presence(cls, planned_on_date, values, **kwargs):
        """

        """
        if planned_on_date is None and values.get('duration') is None:
            raise ValueError('Please specify either "planned_on_date" or "duration" field.')
        else:
            return planned_on_date

