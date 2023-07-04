from typing import Annotated, Literal

from pydantic import Field

from internal.serializers import BaseModel
from models.initial_data import RU_regions

__all__ = (
    'EnterpriseInSerializer',
)


class EnterpriseInSerializer(BaseModel):
    """

    """
    id: Annotated[int | None, Field(ge=1)]
    name: Annotated[str, Field(max_length=256)]
    # noinspection PyTypeHints
    region_name: Literal[*RU_regions.names]
    place: str
    address: Annotated[str, Field(max_length=512)]
    field_of_activity: Annotated[str, Field(max_length=256)]
