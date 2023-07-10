import abc
from decimal import Decimal
from typing import Literal

import shapely.wkt
from geoalchemy2 import WKTElement
from pydantic import field_validator, model_validator, ConfigDict, condecimal, constr

from internal.geo import point_from_numeric
from internal.serializers import BaseModel
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
    coordinates: in_out_coords_format = None


class PlaceDeleteSerializer(BaseModel):
    """
    Для получения данных для удаления Place.
    """
    id: int | None = None
    name: constr(max_length=128) | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_one_field_presence(cls, values):
        """
        Должно быть передано поле id или же name и region_name.
        """
        _id, name = (values.get(key) for key in cls.__fields__.keys())

        if _id is None and name is None:
            raise ValueError(
                    'You should specify either "id" or "name" field.'
                )
        return values

    @property
    def lookup_kwargs(self) -> dict[str, int | str]:
        """
        Отдает маппинг имя поля: значение для последующего нахождения инстанса Place
        по этим данным. Либо мы ищем по id либо по уникальной комбинации name & regin_name.
        """
        return {'id': self.id} if self.id is not None else {'name': self.name}


class PlaceInSerializer(PlaceBaseSerializer):
    """
    Для получения данных Place с фронта.
    """
    id: int | None = None  # None в случае create, int в случае update

    # noinspection PyNestedDecorators
    @field_validator('coordinates')
    @classmethod
    def convert_input_coordinates_into_point(cls, value) -> WKTElement | None:
        """
        Конвертируем координаты в POINT для последующего сохранения в БД.
        """
        return point_from_numeric(*value) if value is not None else None


class RegionOutSerializer(BaseModel):
    """
    Для отдачи Region на фронт.
    """
    name: str = Literal[*RU_regions.names]
    model_config = ConfigDict(from_attributes=True)


class PlaceOutSerializer(PlaceBaseSerializer):
    """
    Для отдачи сохраненного Place на фронт.
    """
    id: int
    region: RegionOutSerializer | None = None
    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)

    @field_validator('coordinates', mode="before")
    @classmethod
    def convert_input_coordinates_into_point(cls, value) -> in_out_coords_format:
        """
        Преобразуем координаты из WKT в широту и долготу.
        """
        if value is None:
            return value
        else:
            shapely_point = shapely.wkt.loads(value.data)
            return Decimal(shapely_point.y), Decimal(shapely_point.x)
