from typing import TYPE_CHECKING

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import defer

from crud.helpers import commit_if_not_in_transaction
from models import Union

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from fastapi_pagination.bases import AbstractParams


__all__ = (
    'get_unions',
)


@commit_if_not_in_transaction
async def get_unions(session: 'AsyncSession', ids: list[int], params: 'AbstractParams') -> list[Union]:
    """
    Возвращает записи Union.
    """
    stmt = select(Union).order_by('id').options(defer(Union.updated_at))
    if ids:
        stmt = stmt.where(Union.id.in_(ids))

    return await paginate(session, stmt, params)
