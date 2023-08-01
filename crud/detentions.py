# https://markandruth.co.uk/2022/12/20/using-postgres-notify-with-placeholders
# https://wuilly.com/2019/10/real-time-notifications-with-python-and-postgres/
    # https://stackoverflow.com/questions/24285563/waiting-for-a-row-update-or-row-insertion-with-sqlalchemy
#c = await session.connection()
# r = await c.get_raw_connection()
# r.driver_connection
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from models import Detention, Jail

__all__ = (
    'zk_for_lawyer',
)


async def zk_for_lawyer(session, regions, start_date, jail_ids):
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

    zk = await session.scalars(stmt)
    return zk.all()
