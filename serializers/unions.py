import datetime

from pydantic import BaseModel

__all__ = (
    'UnionOutSerializer',
)


class UnionOutSerializer(BaseModel):
    """
    Для отдачи инстансов Union на фронт.
    """
    id: int
    name: str
    is_yellow: bool
    created_at: datetime.datetime

    class Config:
        orm_mode = True
