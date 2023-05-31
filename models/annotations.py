from typing import Annotated

from sqlalchemy import Identity
from sqlalchemy.orm import mapped_column

from internal.typing_and_types import BigIntType

__all__ = (
    'BigIntPk',
)

BigIntPk = Annotated[
    BigIntType,
    mapped_column(Identity(always=True), primary_key=True),
]
