import datetime

from internal.serializers import BaseModel
from pydantic import ConfigDict

__all__ = (
    'UnionOutSerializer',
    'UnionInSerializer',
)


class UnionBaseSerializer(BaseModel):
    """
    Базовый сериалайзер Union.
    """
    name: str
    is_yellow: bool | None = None
    id: int | None = None


class UnionInSerializer(UnionBaseSerializer):
    """
    Для получения данных для создания / обновления Union с фронта.
    """
    pass


class UnionOutSerializer(UnionBaseSerializer):
    """
    Для отдачи инстансов Union на фронт.
    """
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
