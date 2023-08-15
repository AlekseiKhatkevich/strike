import datetime

from google.protobuf.internal.well_known_types import Timestamp
from pydantic import ConfigDict, field_validator

from internal.serializers import BaseModel
from models.conflicts import ConflictTypes

__all__ = (
    'ConflictBaseSerializer',
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
    def double(cls, value: Timestamp) -> datetime.datetime | None:
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

    model_config = ConfigDict(from_attributes=True)
