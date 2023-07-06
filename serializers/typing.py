from typing import Annotated

from pydantic import Field

__all__ = (
    'IntIdType',
)

IntIdType = Annotated[int, Field(ge=1)]
