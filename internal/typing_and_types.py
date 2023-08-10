from typing import ClassVar, NewType, Protocol, TypeVar

__all__ = (
    'BigIntType',
    'MODEL_T',
    'ID_T',
    'DataclassType',
)

BigIntType = NewType('BigIntType', int)  # 32 битовый интегер
MODEL_T = TypeVar('MODEL_T', bound='Base')
ID_T = TypeVar('ID_T')


class DataclassType(Protocol):
    __dataclass_fields__: ClassVar[dict]
