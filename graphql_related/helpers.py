import dataclasses
from typing import TYPE_CHECKING, Type

from internal.typing_and_types import DataclassType

if TYPE_CHECKING:
    from internal.database import Base

__all__ = (
    'type_from_model_instance',
)


# noinspection PyArgumentList,PyDataclass
def type_from_model_instance(strawberry_type: Type[DataclassType], so_instance: 'Base') -> DataclassType:
    """
    Создает инстанс strawberry.type из экз. кл. модели.
    """
    f_names = [f.name for f in dataclasses.fields(strawberry_type)]
    return strawberry_type(**{f_name: getattr(so_instance, f_name) for f_name in f_names})
