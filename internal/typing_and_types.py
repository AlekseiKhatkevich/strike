from typing import NewType, TypeVar

__all__ = (
    'BigIntType',
    'MODEL_T',
    'ID_T',
)

BigIntType = NewType('BigIntType', int)  # 32 битовый интегер
MODEL_T = TypeVar('MODEL_T', bound='Base')
ID_T = TypeVar('ID_T')
