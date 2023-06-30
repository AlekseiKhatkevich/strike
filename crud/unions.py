from typing import TYPE_CHECKING

from sqlalchemy import ScalarResult, select

from crud.helpers import commit_if_not_in_transaction
from models import Union

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


__all__ = (
    'get_unions',
)


@commit_if_not_in_transaction
async def get_unions(session: 'AsyncSession', ids: list[int]) -> ScalarResult[Union]:
    """
    Возвращает записи Union.
    """
    stmt = select(Union)
    if ids:
        stmt = stmt.where(Union.id.in_(ids))

    return await session.scalars(stmt)
    # noinspection PyTypeChecker
    # return unions.all()
