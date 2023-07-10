import datetime
from typing import Annotated, Any

from pydantic import (
    field_validator,
    ConfigDict,
    Field,
    PrivateAttr,
    AfterValidator,
    PlainSerializer,
    WithJsonSchema,
    AwareDatetime,
)

from sqlalchemy.dialects.postgresql.ranges import Range

from internal.serializers import BaseModel
from models import UserRole
from serializers.enterprises import EnterpriseInSerializer
from serializers.places import PlaceInSerializer
from serializers.typing import IntIdType

__all__ = (
    'StrikeInSerializer',
    'StrikeOutSerializer',
)


class UsersInvolvedInSerializer(BaseModel):
    """
    Для получения с фронта данных о юзере для создания м2м связи м/у юзером и страйком.
    (вспомогательный).
    """
    user_id: IntIdType
    role: UserRole

    @field_validator('role', mode='before')
    @classmethod
    def _role_upper(cls, role: str) -> str:
        """
        Преобразуем роль юзера в апперкейс так как ENUM требует именно так.
        """
        return role.upper()


def range_validator(value):
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


class StrikeBaseSerializer(BaseModel):
    """
    Базовый сериалайзер Stike.
    """
    duration: RangeField | None = None
    planned_on_date: datetime.date | None = None
    goals: str
    results: str | None = None
    overall_num_of_employees_involved: IntIdType
    union_in_charge_id: IntIdType | None = None


class StrikeInSerializer(StrikeBaseSerializer):
    """
    Сериалайзер для создания Strike и некоторых связанных с ним записей (опционально).
    """
    enterprise: IntIdType | EnterpriseInSerializer
    group: list[IntIdType] | None = None
    places: list[IntIdType | PlaceInSerializer] | None = None
    users_involved: list[UsersInvolvedInSerializer] | None = None
    _created_by_id = PrivateAttr()

    @field_validator('planned_on_date')
    @classmethod
    def _validate_duration_or_planned_on_date_presence(cls,
                                                       planned_on_date: datetime.date | None,
                                                       values: dict[str, Any],
                                                       **kwargs,
                                                       ) -> datetime.date | None:
        """
        Поля "planned_on_date" и "duration" не могут быть None одновременно.
        """
        if planned_on_date is None and values.data.get('duration') is None:
            raise ValueError('Please specify either "planned_on_date" or "duration" field.')
        else:
            return planned_on_date


class StrikeOutSerializer(StrikeBaseSerializer):
    """
    Для отдачи Strike на фронт.
    """
    id: int
    enterprise_id: int
    group_ids: list[int] = []
    created_by_id: int
    users_involved_ids: list[int] = []
    places_ids: Annotated[list[int], Field(alias='places_ids_list')] = []

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    # noinspection PyNestedDecorators
    @field_validator('duration', mode='before')
    @classmethod
    def _duration_to_list(cls, duration):
        if isinstance(duration, Range):
            return [getattr(duration, attr, None) for attr in ('lower', 'upper',)]
        else:
            return duration
