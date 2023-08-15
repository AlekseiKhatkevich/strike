import datetime
from typing import Annotated

from google.protobuf.internal.well_known_types import Timestamp
from pydantic import ConfigDict, field_validator
from pydantic.functional_validators import AfterValidator, BeforeValidator

from internal.serializers import BaseModel
from models.conflicts import ConflictTypes
from serializers.proto.compiled.conflicts_pb2 import ConflictTypes as PBConflictTypes
from serializers.typing import IntIdType

__all__ = (
    'ConflictCreateSerializer',
)

#  преобразуем "" в None так как с protobuf приходит "" в качестве дефолтного значения для str
EmptyStrToNone = Annotated[str | None, BeforeValidator(lambda v: v or None)]
#  преобразуем 0.0 в None так как с protobuf приходит 0.0 в качестве дефолтного значения для float
ZeroFloatToNone = Annotated[
    float | None,
    BeforeValidator(lambda v: v or None),
    AfterValidator(lambda v: round(v, 2) if v else v),
]


class ProtoDurationSerializer(BaseModel):
    """
    Длительность между datetime1 и datetime2.
    """
    lower: Timestamp  # тип protobuf
    upper: Timestamp

    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
    )

    # noinspection PyNestedDecorators
    @field_validator('lower', 'upper')
    @classmethod
    def _convert_ts_into_dt(cls, value: Timestamp) -> datetime.datetime | None:
        """
        Преобразуем пустые таймстампы в None.
        """
        return value.ToDatetime(tzinfo=datetime.UTC) if value.ByteSize() else None


class ConflictBaseSerializer(BaseModel):
    """
    Базовый сериалайзер для 1 конфликта.
    """
    type: ConflictTypes
    duration: ProtoDurationSerializer
    enterprise_id: IntIdType
    description: str
    results: EmptyStrToNone
    success_rate: ZeroFloatToNone

    model_config = ConfigDict(from_attributes=True)

    # noinspection PyNestedDecorators
    @field_validator('type', mode='before')
    @classmethod
    def _get_enum_by_num(cls, value: int) -> ConflictTypes:
        """
        Получаем члена ENUM ConflictTypes модели Conflict через номер ConflictTypes протобафа.
        """
        pb_enum_name = PBConflictTypes.Name(value)
        return getattr(ConflictTypes, pb_enum_name)


class ConflictCreateSerializer(ConflictBaseSerializer):
    """
    Сериалайзер для валидации и преобразования данных от буфера для ЭП CreateConflict.
    """
    pass

