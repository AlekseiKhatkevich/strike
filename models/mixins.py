import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy_utils import refresh_materialized_view
from sqlalchemy_utils.view import CreateView, DropView

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from alembic import op

__all__ = (
    'UpdatedAtMixin',
    'CreatedAtMixin',
    'CreatedUpdatedMixin',
    'MaterializedViewMixin',
)


class UpdatedAtMixin:
    updated_at: Mapped[datetime.datetime | None] = mapped_column(
        onupdate=datetime.datetime.now(tz=datetime.UTC)
    )


class CreatedAtMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(),
    )


class CreatedUpdatedMixin(CreatedAtMixin, UpdatedAtMixin):
    pass


# noinspection PyUnresolvedReferences
class MaterializedViewMixin:
    """
    Для создания, удаления и обновления материализованных представлений.
    """
    @classmethod
    def refresh(cls, session: 'AsyncSession', concurrently: bool = True) -> None:
        refresh_materialized_view(session, cls.__table__.fullname, concurrently)

    @classmethod
    def create(cls, op: 'op') -> None:
        cls.drop(op)
        create_sql = CreateView(cls.__table__.fullname, cls._selectable, materialized=True)
        op.execute(create_sql)
        for idx in cls.__table__.indexes:
            idx.create(op.get_bind())

    @classmethod
    def drop(cls, op: 'op') -> None:
        drop_sql = DropView(cls.__table__.fullname, materialized=True, cascade=True)
        op.execute(drop_sql)
