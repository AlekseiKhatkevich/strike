import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


__all__ = (
    'UpdatedAtMixin',
)


class UpdatedAtMixin:
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        onupdate=func.now(),
    )
