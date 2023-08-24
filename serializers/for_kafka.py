from pydantic import ConfigDict

from shapely import Point

from internal.serializers import BaseModel
from serializers.typing import IntIdType

__all__ = (
    'KafkaCoordinatesSerializer',
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
