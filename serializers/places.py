import abc
from decimal import Decimal
from typing import Literal

import shapely.wkt
from geoalchemy2 import WKTElement
from pydantic import BaseModel, constr, validator, condecimal, root_validator

from internal.geo import point_from_numeric
from models.initial_data import RU_regions

__all__ = (
    'PlaceInSerializer',
    'PlaceOutSerializer',
    'PlaceDeleteSerializer',
)

lat_decimal = condecimal(ge=Decimal(-90), le=Decimal(90))
lon_decimal = condecimal(ge=Decimal(-180), le=Decimal(180))
in_out_coords_format = tuple[lat_decimal, lon_decimal] | None


class PlaceBaseSerializer(BaseModel, abc.ABC):
    """
    Базовый сериалайзер для модели Place.
    """
    name: constr(max_length=128)
    address: constr(max_length=256)
    # noinspection PyTypeHints
    region_name: Literal[*RU_regions.names]
    coordinates: in_out_coords_format


class PlaceDeleteSerializer(BaseModel):
    """
    Для получения данных для удаления Place.
    """
    id: int | None
    name: constr(max_length=128) | None
    # noinspection PyTypeHints
    region_name: Literal[*RU_regions.names] | None

    @root_validator(pre=True)
    def validate_one_field_presence(cls, values):
        """
        Должно быть передано поле id или же name и region_name.
        """
        _id, name, region_name = (values.get(key) for key in cls.__fields__.keys())

        if _id is None and (name is None or region_name is None):
            raise ValueError(
                    'You should specify either "id" or both "name" and "region_name" fields.'
                )
        return values

    @property
    def lookup_kwargs(self) -> dict[str, int | str]:
        """
        Отдает маппинг имя поля: значение для последующего нахождения инстанса Place
        по этим данным. Либо мы ищем по id либо по уникальной комбинации name & regin_name.
        """
        return {'id': self.id} if self.id is not None else {'name': self.name, 'region_name': self.region_name}


class PlaceInSerializer(PlaceBaseSerializer):
    """
    Для получения данных Place с фронта.
    """
    id: int | None  # None в случае create, int в случае update

    @validator('coordinates')
    def convert_input_coordinates_into_point(cls, value) -> WKTElement | None:
        """
        Конвертируем координаты в POINT для последующего сохранения в БД.
        """
        return point_from_numeric(*value) if value is not None else None

    class Config:
        anystr_strip_whitespace = True
        min_anystr_length = 1
        frozen = True
        allow_mutation = False


class PlaceOutSerializer(PlaceBaseSerializer):
    """
    Для отдачи сохраненного Place на фронт.
    """
    id: int

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True

    @validator('coordinates', pre=True)
    def convert_input_coordinates_into_point(cls, value) -> in_out_coords_format:
        """
        Преобразуем координаты из WKT в широту и долготу.
        """
        if value is None:
            return value
        else:
            shapely_point = shapely.wkt.loads(value.data)
            return Decimal(shapely_point.y), Decimal(shapely_point.x)
