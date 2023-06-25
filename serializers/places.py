from decimal import Decimal
from typing import Literal

from geoalchemy2 import WKTElement
from pydantic import BaseModel, constr, validator, condecimal

from internal.geo import point_from_numeric
from models.initial_data import RU_regions

__all__ = (
    'PlaceInSerializer',
)

lat_decimal = condecimal(ge=Decimal(-180), le=Decimal(180))
lon_decimal = condecimal(ge=Decimal(-90), le=Decimal(90))


class PlaceInSerializer(BaseModel):
    """
    Для отдачи основных данных юзера.
    """
    name: constr(max_length=128)
    address: constr(max_length=256)
    # noinspection PyTypeHints
    region_name: Literal[*RU_regions.names]
    coordinates: tuple[lat_decimal, lon_decimal] | None

    class Config:
        anystr_strip_whitespace = True
        min_anystr_length = 1
        frozen = True
        allow_mutation = False

    @validator('coordinates')
    def convert_input_coordinates_into_point(cls, value) -> WKTElement | None:
        """
        Конвертируем координаты в POINT для последующего сохранения в БД.
        """
        return point_from_numeric(*value) if value is not None else None
