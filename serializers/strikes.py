import datetime
from typing import Annotated, Self

from pydantic import (
    field_validator,
    ConfigDict,
    Field,
    PrivateAttr,
    AfterValidator,
    PlainSerializer,
    WithJsonSchema,
    AwareDatetime,
    model_validator,
)

from sqlalchemy.dialects.postgresql.ranges import Range

from internal.serializers import BaseModel
from models import UserRole
from serializers.enterprises import EnterpriseInSerializer
from serializers.places import PlaceInSerializer
from serializers.typing import IntIdType

__all__ = (
    'StrikeInSerializer',
    'StrikeOutSerializerFull',
    'StrikeUpdateInSerializer',
    'StrikeOutSerializerShort',
    'AddRemoveStrikeM2MObjectsSerializer',
    'AddRemoveUsersInvolvedSerializer',
    'UsersInvolvedOutSerializer',
)


class UsersInvolvedInSerializer(BaseModel):
    """
    Для получения с фронта данных о юзере для создания м2м связи м/у юзером и страйком.
    (вспомогательный).
    """
    user_id: IntIdType
    role: UserRole

    # noinspection PyNestedDecorators
    @field_validator('role', mode='before')
    @classmethod
    def _role_upper(cls, role: str) -> str:
        """
        Преобразуем роль юзера в апперкейс так как ENUM требует именно так.
        """
        return role.upper()


class UsersInvolvedOutSerializer(BaseModel):
    """
    Для отдачи инфы о юзерах вовлеченных в забастовку на ЭП /strikes/{id:int}/users_involved.
    """
    user_id: int
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


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

    _dates_mutual_none_exc_text = 'Please specify either "planned_on_date" or "duration" field.'

    # noinspection PyNestedDecorators
    @model_validator(mode='before')
    @classmethod
    def dates_mutual_none_exc(cls, data):
        """
        Поля planned_on_date и duration не могут быть None одновременно если они передаются
        с фронта.
        """
        try:
            planned_on_date = data['planned_on_date']
            duration = data['duration']
        except (KeyError, TypeError):  # если нет хотя бы одного поля - то с фронта они не пришли оба.
            pass
        else:
            #  оба поля пришли с фронта, а не из defaults
            if planned_on_date is None and duration is None:
                raise ValueError(cls._dates_mutual_none_exc_text)
        return data


class StrikeUpdateInSerializer(StrikeBaseSerializer):
    """
    Сериалайзер для обновления записи Strike.
    """
    goals: str = None
    overall_num_of_employees_involved: IntIdType = None
    enterprise_id: IntIdType = None


class StrikeInSerializer(StrikeBaseSerializer):
    """
    Сериалайзер для создания Strike и некоторых связанных с ним записей (опционально).
    """
    enterprise: IntIdType | EnterpriseInSerializer
    group: list[IntIdType] | None = None
    places: list[IntIdType | PlaceInSerializer] | None = None
    users_involved: list[UsersInvolvedInSerializer] | None = None
    _created_by_id = PrivateAttr()


class StrikeOutSerializerBase(StrikeBaseSerializer):
    """
    Базовый сериалайзер для отдачи Strike на фронт.
    """
    id: int
    enterprise_id: int
    created_by_id: int

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    # noinspection PyNestedDecorators
    @field_validator('duration', mode='before')
    @classmethod
    def _duration_to_list(cls,
                          duration: Range | list[AwareDatetime | None] | None,
                          ) -> list[AwareDatetime | None] | None:
        """
        Преобразуем на входе Range в лист с datetime если нужно.
        """
        if isinstance(duration, Range):
            return [getattr(duration, attr, None) for attr in ('lower', 'upper',)]
        else:
            return duration


class StrikeOutSerializerFull(StrikeOutSerializerBase):
    """
    Для отдачи данных о Strike с доп. данными связей м2м.
    """
    group_ids: list[int] = []
    users_involved_ids: list[int] = []
    places_ids: Annotated[list[int], Field(alias='places_ids_list')] = []


class StrikeOutSerializerShort(StrikeOutSerializerBase):
    """
    Для отдачи данных о Strike.
    """
    pass


class AddRemoveStrikeM2MObjectsBaseSerializer(BaseModel):
    """
    Базовый сериалайзер для создания / удаления м2м связей Strike с другими моделями и
    самим с собой.
    """
    add: set[IntIdType] = set()
    remove: set[IntIdType] = set()

    # noinspection PyNestedDecorators
    @model_validator(mode='after')
    @classmethod
    def no_intersection(cls, serializer: Self) -> Self:
        """
        Проверяет, чтобы id переданные на создание и на удаление не пересекались.
        """
        if intersection := cls.get_intersection(serializer):
            raise ValueError(
                f'These ids {intersection} are common to both "add" and "remove" fields. '
                f'They should be either added or removed, not both simultaneously!'
            )
        else:
            return serializer

    def get_intersection(self) -> set[id, ...]:
        """
        Пересечение add и remove.
        """
        return self.add.intersection(self.remove)


class AddRemoveStrikeM2MObjectsSerializer(AddRemoveStrikeM2MObjectsBaseSerializer):
    """
    Для добавления/ удаления м2м связей в Strike.
    """
    pass


class AddRemoveUsersInvolvedSerializer(AddRemoveStrikeM2MObjectsBaseSerializer):
    """
    Для м2м связей users_involved Strike <-> User.
    """
    add: list[UsersInvolvedInSerializer] = []

    def get_intersection(self):
        return self.remove.intersection(
            inner_s.user_id for inner_s in self.add
        )
