from typing import NoReturn, TYPE_CHECKING

from fastapi import HTTPException, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import Integer, delete, exc as sa_exc, func, select
from sqlalchemy.dialects.postgresql import ARRAY, insert
from sqlalchemy.orm import joinedload, load_only, selectinload, with_expression

from crud.helpers import flush_and_raise, get_id_from_integrity_error
from models import (
    Enterprise,
    Place,
    Strike,
    StrikeToItself,
    StrikeToPlaceAssociation,
)
from models.exceptions import ModelEntryDoesNotExistsInDbError

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from serializers.strikes import (
        AddRemoveStrikeM2MObjectsSerializer,
        StrikeInSerializer,
        AddRemoveUsersInvolvedSerializer,
    )
    from fastapi_pagination.bases import AbstractParams

__all__ = (
    'create_strike',
    'manage_group',
    'manage_places',
    'manage_users_involved',
    'get_strikes',
)


def _raise_strike_does_not_exists(strike_id) -> NoReturn:
    """
    Рейзит исключение если страйк не найден.
    """
    raise ModelEntryDoesNotExistsInDbError(
        f'Strike with id {strike_id} does not exists',
        report=True,
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
                places_ids.add(new_place_data)
                strike_instance.places_ids_list.append(new_place_data)
            else:
                places = await strike_instance.awaitable_attrs.places
                places.append(place := Place(**new_place_data.model_dump(exclude={'id', })))
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
        users_involved.add(user_data.model_dump())
        strike_instance.users_involved_ids.append(user_data.user_id)


async def create_strike(session: 'AsyncSession', strike_data: 'StrikeInSerializer') -> Strike:
    """
    Создание записи Strike и ассоциированных с ней записей.
    """
    # noinspection PyProtectedMember
    strike_instance = Strike(
        **strike_data.model_dump(exclude={'group', 'places', 'users_involved', 'enterprise'}),
        created_by_id=strike_data._created_by_id,
    )
    if isinstance(strike_data.enterprise, int):
        strike_instance.enterprise_id = strike_data.enterprise
    else:
        enterprise_instance = Enterprise(**strike_data.enterprise.model_dump(exclude={'id', }))
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

    if hasattr(strike_instance, 'places_ids_list'):
        strike_instance.places_ids_list = [
            p.id if isinstance(p, Place) else p for p in strike_instance.places_ids_list
        ]
    else:
        strike_instance.places_ids_list = []

    return strike_instance


async def manage_group(session: 'AsyncSession',
                       strike_id: int,
                       m2m_ids: 'AddRemoveStrikeM2MObjectsSerializer',
                       ) -> list[int, ...]:
    """
    Добавление / удаление забастовки в группу.
    """
    to_add = [
        dict(strike_left_id=strike_id, strike_right_id=group_id) for group_id in m2m_ids.add
        if group_id != strike_id
    ]
    if to_add:
        add_stmt = insert(StrikeToItself).values(to_add).on_conflict_do_nothing()
        await session.execute(add_stmt)

    if m2m_ids.remove:
        del_stmt = delete(StrikeToItself).where(
            StrikeToItself.strike_left_id == strike_id,
            StrikeToItself.strike_right_id.in_(m2m_ids.remove)
        )
        await session.execute(del_stmt)

    group_ids = await session.scalars(
        select(StrikeToItself.strike_right_id).where(StrikeToItself.strike_left_id == strike_id)
    )
    await session.commit()
    # noinspection PyTypeChecker
    return group_ids.all()


async def manage_places(session: 'AsyncSession',
                        strike_id: int,
                        m2m_ids: 'AddRemoveStrikeM2MObjectsSerializer',
                        ) -> set[int, ...]:
    """
    Добавление / удаление м2м связи забастовка <-> место.
    """
    strike = await session.scalar(
        select(Strike).options(
            selectinload(Strike.places_association_recs).options(
                load_only(StrikeToPlaceAssociation.place_id, raiseload=True)
            )
        ).where(Strike.id == strike_id))

    if strike is None:
        _raise_strike_does_not_exists(strike_id)

    places_ids = strike.places_ids
    places_ids.update(m2m_ids.add)
    places_ids.difference_update(m2m_ids.remove)

    await session.commit()
    return places_ids


async def manage_users_involved(session: 'AsyncSession',
                                strike_id: int,
                                m2m: 'AddRemoveUsersInvolvedSerializer',
                                ) -> set[int, ...]:
    """
    Добавление / удаление м2м связи забастовка <-> юзер.
    """
    strike = await session.scalar(
        select(
            Strike
        ).options(
            selectinload(Strike.users_involved)
        ).where(
            Strike.id == strike_id
        )
    )
    if strike is None:
        _raise_strike_does_not_exists(strike_id)

    relation = strike.users_involved_create
    for inner_s in m2m.add:
        if inner_s.user_id not in relation:
            relation.add(inner_s.model_dump())

    relation.difference_update(m2m.remove)

    await session.commit()
    return strike.users_involved


async def get_strikes(session: 'AsyncSession',
                      ids: list[int, ...],
                      params: 'AbstractParams',
                      *,
                      only_active: bool,
                      ) -> list[Strike, ...]:
    """
    Для отдачи данных о страйке на фронт.
    ids - список id которые нужно отдать. Если не указанно - то все.
    only_active - только те страйки которые сейчас активны на данный момент. Так же это
    относиться и к страйкам в группе.
    """
    group_ids_subquery = select(
        func.array_agg(StrikeToItself.strike_right_id, type_=ARRAY(Integer))
    ).where(
        Strike.id == StrikeToItself.strike_left_id
    ).group_by(
        StrikeToItself.strike_left_id,
    ).scalar_subquery()

    stmt = select(
        Strike
    ).order_by(
        Strike.duration,
        Strike.planned_on_date,
    ).options(
        joinedload(Strike.union),
        joinedload(Strike.enterprise, innerjoin='unnested'),
        with_expression(Strike.group_ids_from_exp, group_ids_subquery),
        selectinload(Strike.users_involved),
        selectinload(Strike.places).options(joinedload(Place.region)),
    ).execution_options(
        populate_existing=True,
    )

    if ids:
        stmt = stmt.where(Strike.id.in_(ids))
    if only_active:
        stmt = stmt.where(Strike.is_active == True)

    res = await paginate(session, stmt, params, unique=True)
    return res
