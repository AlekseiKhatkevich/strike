from typing import TYPE_CHECKING

from models import Enterprise, Place, Strike, StrikeToItself

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

    if strike_data.places is not None:
        for new_place_data in strike_data.places:
            if isinstance(new_place_data, int):
                places_ids = await strike_instance.awaitable_attrs.places_ids
                places_ids.append(new_place_data)
            else:
                places = await strike_instance.awaitable_attrs.places
                places.append(Place(**new_place_data.dict(exclude={'id', })))

    if strike_data.users_involved is not None:
        for user_data in strike_data.users_involved:
            users_involved = await strike_instance.awaitable_attrs.users_involved_create
            users_involved.append(user_data.dict())

    if strike_data.group is not None:
        session.add_all(
            StrikeToItself(strike_left_id=strike_instance.id, strike_right_id=group_id)
            for group_id in strike_data.group
        )

    await session.commit()

    return strike_instance
