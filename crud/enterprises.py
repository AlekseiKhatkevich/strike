from typing import TYPE_CHECKING

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from crud.helpers import commit_if_not_in_transaction
from models import Enterprise

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from fastapi_pagination.bases import AbstractParams


__all__ = (
    'get_enterprises',
)


@commit_if_not_in_transaction
async def get_enterprises(session: 'AsyncSession',
                          ids: list[int],
                          params: 'AbstractParams',
                          ) -> list[Enterprise]:
    """
    Отдает 1 или несколько записей Enterprise с пагинацией.
    """
    stmt = select(Enterprise).order_by('id')
    if ids:
        stmt = stmt.where(Enterprise.id.in_(ids))

    return await paginate(session, stmt, params)
