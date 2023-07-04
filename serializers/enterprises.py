import datetime
from typing import Annotated, Literal

from pydantic import Field

from internal.serializers import BaseModel
from models.initial_data import RU_regions

__all__ = (
    'EnterpriseInSerializer',
    'EnterpriseOutSerializer',
)


class EnterpriseBaseSerializer(BaseModel):
    """
    Базовый сериалайзер для модели Enterprise.
    """
    id: Annotated[int | None, Field(ge=1)]
    name: Annotated[str, Field(max_length=256)]
    # noinspection PyTypeHints
    region_name: Literal[*RU_regions.names]
    place: str
    address: Annotated[str, Field(max_length=512)]
    field_of_activity: Annotated[str | None, Field(max_length=256)]


class EnterpriseInSerializer(EnterpriseBaseSerializer):
    """
    Сериалайзер для получения данных Enterprise с фронта.
    """
    pass


class EnterpriseOutSerializer(EnterpriseBaseSerializer):
    """
    Сериалайзер для отправки данных об инстансе Enterprise на фронт.
    """
    created_at: datetime.datetime
    updated_at: datetime.datetime | None

    class Config:
        orm_mode = True
