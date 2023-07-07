from typing import TYPE_CHECKING

from fastapi import HTTPException, status
from sqlalchemy import exc as sa_exc

from crud.helpers import flush_and_raise, get_id_from_integrity_error
from models import Enterprise, Place, Strike, StrikeToItself

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from serializers.strikes import StrikeInSerializer

__all__ = (
    'create_strike',
)


async def add_places(strike_data, strike_instance):
    """

    """
    try:
        for new_place_data in strike_data.places:
            if isinstance(new_place_data, int):
                places_ids = await strike_instance.awaitable_attrs.places_ids
                places_ids.append(new_place_data)
            else:
                places = await strike_instance.awaitable_attrs.places
                places.append(Place(**new_place_data.dict(exclude={'id', })))
    except sa_exc.IntegrityError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Place id {get_id_from_integrity_error(err)} does not exists.',
        ) from err


async def add_users(strike_data, strike_instance):
    """

    """
    for user_data in strike_data.users_involved:
        users_involved = await strike_instance.awaitable_attrs.users_involved_create
        users_involved.append(user_data.dict())


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
        await add_places(strike_data, strike_instance)

    if strike_data.users_involved is not None:
        await add_users(strike_data, strike_instance)

    if strike_data.group is not None:
        session.add_all(
            StrikeToItself(strike_left_id=strike_instance.id, strike_right_id=group_id)
            for group_id in strike_data.group
        )

    await flush_and_raise(session, 'Strike id {id} does not exists.')

    await session.commit()

    return strike_instance
