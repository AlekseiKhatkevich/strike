import datetime
from typing import Annotated
from sqlalchemy.dialects.postgresql.ranges import Range
from pydantic import Field, validator

from internal.serializers import BaseModel
from models import UserRole

from serializers.enterprises import EnterpriseInSerializer
from serializers.places import PlaceInSerializer

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


class UsersInvolvedInSerializer(BaseModel):
    """

    """
    user_id: Annotated[int, Field(ge=1)]
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
    overall_num_of_employees_involved: Annotated[int, Field(ge=1)]
    enterprise: Annotated[int, Field(ge=1)] | EnterpriseInSerializer
    union_in_charge_id: Annotated[int | None, Field(ge=1)]
    group: list[Annotated[int, Field(ge=1)]] | None
    places: list[Annotated[int, Field(ge=1)] | PlaceInSerializer] | None
    users_involved: list[UsersInvolvedInSerializer] | None

    @validator('planned_on_date', always=True)
    def _validate_duration_or_planned_on_date_presence(cls, planned_on_date, values, **kwargs):
        """

        """
        if planned_on_date is None and values['duration'] is None:
            raise ValueError('Please specify either "planned_on_date" or "duration" field.')
        else:
            return planned_on_date
