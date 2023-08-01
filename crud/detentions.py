from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from models import Detention, Jail

__all__ = (
    'zk_for_lawyer',
)


async def zk_for_lawyer(session, regions, start_date, jail_ids, last_id=None):
    """

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

    stmt = stmt.options(joinedload(join_on, innerjoin=True),)

    if last_id is not None:
        stmt = stmt.where(Detention.id > last_id)

    zk = await session.scalars(stmt)
    return zk.all()
