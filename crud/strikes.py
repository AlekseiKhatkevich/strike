from typing import TYPE_CHECKING

from models import Enterprise, Strike, StrikeToItself

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from serializers.strikes import StrikeInSerializer

__all__ = (
    'create_strike',
)


async def create_strike(session: 'AsyncSession', strike_data: 'StrikeInSerializer'):
    """

    """
    # noinspection PyProtectedMember
    strike_instance = Strike(
        **strike_data.dict(exclude={'group', 'places', 'users_involved', 'enterprise'}),
        created_by_id=strike_data._created_by_id,
    )
    if isinstance(strike_data.enterprise, int):
        strike_instance.enterprise_id = strike_data.enterprise
    else:
        enterprise_instance = Enterprise(**strike_data.enterprise.dict(exclude={'id', }))
        strike_instance.enterprise = enterprise_instance

    session.add(strike_instance)
    await session.flush()

    if strike_data.group is not None:
        session.add_all(
            StrikeToItself(strike_left_id=strike_instance.id, strike_right_id=group_id)
            for group_id in strike_data.group
        )


    await session.commit()
    return strike_instance
