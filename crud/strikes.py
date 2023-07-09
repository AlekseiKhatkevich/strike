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


async def add_places(strike_data: 'StrikeInSerializer', strike_instance: Strike) -> None:
    """
    Добавляет м2м связь с Place и если нужно то и создает Place также.
    """
    try:
        strike_instance.places_ids_list = []
        for new_place_data in strike_data.places:
            if isinstance(new_place_data, int):
                places_ids = await strike_instance.awaitable_attrs.places_ids
                places_ids.append(new_place_data)
                strike_instance.places_ids_list.append(new_place_data)
            else:
                places = await strike_instance.awaitable_attrs.places
                places.append(place := Place(**new_place_data.dict(exclude={'id', })))
                strike_instance.places_ids_list.append(place)
    except sa_exc.IntegrityError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Place id {get_id_from_integrity_error(err)} does not exists.',
        ) from err


async def add_users(strike_data: 'StrikeInSerializer', strike_instance: Strike) -> None:
    """
    Добавляет юзеров через м2м к текущей создаваемой записи Strike.
    """
    strike_instance.users_involved_ids = []
    users_involved = await strike_instance.awaitable_attrs.users_involved_create
    for user_data in strike_data.users_involved:
        users_involved.append(user_data.dict())
        strike_instance.users_involved_ids.append(user_data.user_id)


async def create_strike(session: 'AsyncSession', strike_data: 'StrikeInSerializer'):
    """
    Создание записи Strike и ассоциированных с ней записей.
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
        strike_instance.group_ids = strike_data.group

    await flush_and_raise(session, 'Strike id {id} does not exists.')

    await session.commit()

    strike_instance.places_ids_list = [p.id if isinstance(p, Place) else p for p in strike_instance.places_ids_list]

    return strike_instance
