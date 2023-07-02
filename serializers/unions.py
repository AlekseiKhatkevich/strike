import datetime

from pydantic import BaseModel

__all__ = (
    'UnionOutSerializer',
    'UnionInSerializer',
)


class UnionBaseSerializer(BaseModel):
    """
    Базовый сериалайзер Union.
    """
    name: str
    is_yellow: bool | None
    id: int | None


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

    class Config:
        orm_mode = True
