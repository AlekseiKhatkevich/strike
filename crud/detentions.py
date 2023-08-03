import datetime
from typing import TYPE_CHECKING

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from models import Detention, DetentionMaterializedView, Jail

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from fastapi_pagination.bases import AbstractParams

__all__ = (
    'zk_for_lawyer',
)


async def zk_for_lawyer(session: 'AsyncSession',
                        regions: list[str, ...],
                        start_date: datetime.datetime,
                        jail_ids: list[int, ...],
                        last_id: int | None = None,
                        ) -> list[Detention, ...]:
    """
    Получение списка задержанных для ЭП '/ws/lawyer'.
    """
    # noinspection PyTypeChecker
    stmt = select(
        Detention,
    ).where(
        func.lower(Detention.duration) >= start_date,
    )

    join_on = Detention.jail
    if regions:
        join_on = join_on.and_(Jail.region_id.in_(regions))
    if jail_ids:
        join_on = join_on.and_(Jail.id.in_(jail_ids))

    stmt = stmt.options(joinedload(join_on, innerjoin=True,),)

    if last_id is not None:
        stmt = stmt.where(Detention.id > last_id)

    zk = await session.scalars(stmt)
    return zk.all()


async def zk_daily_stats(session: 'AsyncSession', params: 'AbstractParams'):
    """
    Получение ежедневной статистики для '/statistics/daily/'.
    """
    stmt = select(
        DetentionMaterializedView,
    ).order_by(
        DetentionMaterializedView.date.desc(),
        DetentionMaterializedView.jail_id,
    )
    return await paginate(session, stmt, params)
