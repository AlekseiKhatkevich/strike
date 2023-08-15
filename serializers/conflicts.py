import datetime

from google.protobuf.internal.well_known_types import Timestamp
from pydantic import ConfigDict, field_validator

from internal.serializers import BaseModel
from models.conflicts import ConflictTypes
from serializers.proto.compiled.conflicts_pb2 import ConflictTypes as PBConflictTypes
from serializers.typing import IntIdType

__all__ = (
    'ConflictCreateSerializer',
)


class ProtoDurationSerializer(BaseModel):
    """

    """
    lower: Timestamp
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

        """
        if not value.ByteSize():  # пустые таймстампы преобразуем в None.
            return None
        else:
            return value.ToDatetime(tzinfo=datetime.UTC)


class ConflictBaseSerializer(BaseModel):
    """

    """
    type: ConflictTypes
    duration: ProtoDurationSerializer
    enterprise_id: IntIdType
    description: str
    results: str | None
    success_rate: float | None

    model_config = ConfigDict(from_attributes=True)

    # noinspection PyNestedDecorators
    @field_validator('type', mode='before')
    @classmethod
    def _get_enum_by_num(cls, value: int) -> ConflictTypes:
        """
        """
        pb_enum_name = PBConflictTypes.Name(value)
        return getattr(ConflictTypes, pb_enum_name)

    # noinspection PyNestedDecorators
    @field_validator('success_rate')
    @classmethod
    def _round_success_rate(cls, value: float) -> float:
        """
        """
        return round(value, 2)


class ConflictCreateSerializer(ConflictBaseSerializer):
    pass

