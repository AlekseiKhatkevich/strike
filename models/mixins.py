import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


__all__ = (
    'UpdatedAtMixin',
    'CreatedAtMixin',
)


class UpdatedAtMixin:
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        onupdate=func.now(),
    )


class CreatedAtMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(),
    )
