from pydantic import ConfigDict, field_validator

from shapely import Point, wkt

from internal.serializers import BaseModel
from serializers.typing import IntIdType

__all__ = (
    'KafkaCoordinatesSerializer',
    'KafkaCoordinatesDeSerializer',
)


class KafkaCoordinatesSerializer(BaseModel):
    """
    Для сериализации данных в KafkaPointsProducer.
    """
    user_id: IntIdType
    point: Point

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={Point: lambda p: p.wkt},
    )


class KafkaCoordinatesDeSerializer(KafkaCoordinatesSerializer):
    """
    Для десериализации данных послед кафки.
    """
    # noinspection PyNestedDecorators
    @field_validator('point', mode='before')
    @classmethod
    def _deserialize_point(cls, point: str) -> Point:
        """
        Десериализуем строковый point в shapely POINT.
        """
        return wkt.loads(point)