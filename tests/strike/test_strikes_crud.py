import pytest
from fastapi import HTTPException
from fastapi_pagination import Params
from sqlalchemy import func, select

from crud.helpers import exists_in_db, is_instance_in_db
from crud.strikes import (
    create_strike,
    get_strikes, manage_group,
    manage_places,
    manage_users_involved,
)
from models import (
    Enterprise,
    Place,
    StrikeToUserAssociation,
    UserRole,
)
from models.exceptions import ModelEntryDoesNotExistsInDbError
from serializers.strikes import (
    AddRemoveStrikeM2MObjectsSerializer,
    AddRemoveUsersInvolvedSerializer,
    StrikeInSerializer,
    UsersInvolvedInSerializer,
)

params = Params(page=1, size=100)

@pytest.fixture
def strike_serializer(strike_input_data, user_in_db) -> StrikeInSerializer:
    """
    Инстанс сериалайзера с минимальным набором данных.
    """
    ser = StrikeInSerializer(**strike_input_data)
    ser._created_by_id = user_in_db.id
    return ser


@pytest.fixture
def strike_serializer_with_new_enterprise(strike_input_data,
                                          enterprise_factory,
                                          user_in_db,
                                          region,
                                          ) -> StrikeInSerializer:
    """
    Инстанс сериалайзера с новой компанией.
    """
    enterprise = enterprise_factory.build(region=region)
    strike_input_data['enterprise'] = enterprise.__dict__
    ser = StrikeInSerializer(**strike_input_data)
    ser._created_by_id = user_in_db.id
    return ser


@pytest.fixture
def strike_serializer_with_new_places(strike_input_data,
                                      place_factory,
                                      user_in_db,
                                      place,
                                      ) -> StrikeInSerializer:
    """
    Инстанс сериалайзера с новыми местами в виде id:int и PlaceInSerializer.
    """
    place_inst = place_factory.build()
    strike_input_data['places'] = [place.id, {'name': place_inst.name, 'address': place_inst.address}, ]
    ser = StrikeInSerializer(**strike_input_data)
    ser._created_by_id = user_in_db.id
    return ser


@pytest.fixture
def strike_serializer_with_group(strike_input_data, user_in_db, strike) -> StrikeInSerializer:
    """
    Инстанс сериалайзера с группой.
    """
    strike_input_data['group'] = [strike.id, ]
    ser = StrikeInSerializer(**strike_input_data)
    ser._created_by_id = user_in_db.id
    return ser


@pytest.fixture
def strike_serializer_with_users_involved(strike_input_data, user_in_db, faker) -> StrikeInSerializer:
    """
    Инстанс сериалайзера c набором вовлеченных юзеров.
    """
    strike_input_data['users_involved'] = [{'user_id': user_in_db.id, 'role': faker.enum(UserRole).value}]
    ser = StrikeInSerializer(**strike_input_data)
    ser._created_by_id = user_in_db.id
    return ser


async def test_create_strike_positive_basic(db_session, strike_serializer):
    """
    Позитивный тест ф-ции CRUD create_strike. Базовый случай с минимумом данных на входе.
    """
    strike_in_db = await create_strike(db_session, strike_serializer)

    assert await is_instance_in_db(db_session, strike_in_db)
    await db_session.refresh(strike_in_db)
    assert [strike_in_db.duration.lower, strike_in_db.duration.upper] == strike_serializer.duration
    assert strike_in_db.goals == strike_serializer.goals
    assert strike_in_db.overall_num_of_employees_involved == strike_serializer.overall_num_of_employees_involved
    assert strike_in_db.union_in_charge_id == strike_serializer.union_in_charge_id
    assert strike_in_db.enterprise_id == strike_serializer.enterprise


async def test_create_strike_positive_new_enterprise(db_session,
                                                     strike_serializer_with_new_enterprise,
                                                     ):
    """
    Позитивный тест ф-ции CRUD create_strike. Вариант с созданием новой компании.
    """
    strike_in_db = await create_strike(db_session, strike_serializer_with_new_enterprise)

    assert await is_instance_in_db(db_session, strike_in_db)
    assert await exists_in_db(db_session, Enterprise, Enterprise.id == strike_in_db.enterprise_id)


async def test_create_strike_positive_new_places(db_session, strike_serializer_with_new_places):
    """
    Позитивный тест ф-ции CRUD create_strike. Вариант с созданием новых Place.
    """
    strike_in_db = await create_strike(db_session, strike_serializer_with_new_places)

    assert await is_instance_in_db(db_session, strike_in_db)
    assert await db_session.scalar(
        select(func.count()).select_from(Place).where(
            (Place.id == strike_serializer_with_new_places.places[0]) |
            (Place.name == strike_serializer_with_new_places.places[-1].name)
        )) == 2
    assert strike_serializer_with_new_places.places[0] in strike_in_db.places_ids_list


async def test_create_strike_positive_with_group(db_session, strike_serializer_with_group):
    """
    Позитивный тест ф-ции CRUD create_strike. Вариант с созданием м2м связи группы.
    """
    strike_in_db = await create_strike(db_session, strike_serializer_with_group)

    assert await is_instance_in_db(db_session, strike_in_db)

    group = await strike_in_db.awaitable_attrs.group

    assert group[0].id == strike_serializer_with_group.group[0]
    assert strike_in_db.group_ids == strike_serializer_with_group.group


async def test_create_strike_positive_with_users_involved(db_session, strike_serializer_with_users_involved):
    """
    Позитивный тест ф-ции CRUD create_strike. Вариант с созданием м2м связи с юзерами.
    """
    strike_in_db = await create_strike(db_session, strike_serializer_with_users_involved)

    assert await is_instance_in_db(db_session, strike_in_db)

    users_involved = await strike_in_db.awaitable_attrs.users_involved

    (entry,) = users_involved
    assert entry.user_id == strike_serializer_with_users_involved.users_involved[0].user_id
    assert strike_in_db.users_involved_ids[0] == strike_serializer_with_users_involved.users_involved[0].user_id


@pytest.mark.parametrize(
    'key, error_message',
    [
        ('places', 'Place id 99999999999 does not exists.'),
        ('group', 'Strike id 99999999999 does not exists.'),
    ]
)
async def test_create_strike_negative(key,
                                      error_message,
                                      db_session,
                                      strike_input_data,
                                      user_in_db,
                                      ):
    """
    Негативный тест ф-ции CRUD create_strike. Что будет если передать неправильный Place.id
     или Strike.id для группы.
    """
    strike_input_data[key] = [99999999999, ]
    ser = StrikeInSerializer(**strike_input_data)
    ser._created_by_id = user_in_db.id

    with pytest.raises(HTTPException) as err:
        await create_strike(db_session, ser)
        assert err.detail == error_message


async def test_manage_places_positive(strike, places_batch, db_session):
    """
    Позитивный тест ф-ции manage_places
    (Добавление / удаление м2м связи забастовка <-> место)
    """
    to_add = {place.id for place in places_batch}
    to_remove = set(await strike.awaitable_attrs.places_ids)
    m2m = AddRemoveStrikeM2MObjectsSerializer(add=to_add, remove=to_remove)

    place_ids = await manage_places(db_session, strike.id, m2m)
    await db_session.refresh(strike, ('places', 'places_association_recs'))

    assert place_ids == to_add
    assert await strike.awaitable_attrs.places_ids == to_add
    assert strike.places_ids.isdisjoint(to_remove)


async def test_manage_places_negative_rem_place_does_not_exists(db_session, strike_p):
    """
    Негативный тест ф-ции manage_places. Случай, если запись Place по переданному id
    не существует.
    """
    strike = await strike_p(num_places=0)
    m2m = AddRemoveStrikeM2MObjectsSerializer(add=set(), remove={1, 2, 3})

    await manage_places(db_session, strike.id, m2m)


async def test_manage_group_positive(strike_p, db_session, strike):
    """
    Позитивный тест ф-ции manage_group.
    """
    strike_with_group = await strike_p(num_group=2)
    strike_to_add = strike
    m2m = AddRemoveStrikeM2MObjectsSerializer(
        add={strike_to_add.id, },
        remove={g_strike.id for g_strike in strike_with_group.group}
    )

    group_ids = await manage_group(db_session, strike_with_group.id, m2m)

    assert group_ids == [strike_to_add.id]


async def test_manage_users_involved_positive(db_session, strike, user_in_db, user_role):
    """
    Позитивный тест ф-ции manage_users_involved.
    """
    to_add = [UsersInvolvedInSerializer(user_id=user_in_db.id, role=user_role.value), ]
    to_remove = set(strike.user_ids)
    m2m = AddRemoveUsersInvolvedSerializer(add=to_add, remove=to_remove)

    users_m2m = await manage_users_involved(db_session, strike.id, m2m)

    assert len(users_m2m) == 1
    (new_entry,) = users_m2m
    assert new_entry.user_id == user_in_db.id

    assert not await exists_in_db(
        db_session,
        StrikeToUserAssociation,
        (StrikeToUserAssociation.strike_id == strike.id) &
        (StrikeToUserAssociation.user_id.in_(to_remove)),
    )
    assert await exists_in_db(
        db_session,
        StrikeToUserAssociation,
        (StrikeToUserAssociation.strike_id == strike.id) &
        (StrikeToUserAssociation.user_id == user_in_db.id)
    )


@pytest.mark.parametrize('crud_f', [manage_users_involved, manage_places])
async def test_manage_users_involved_negative_no_strike(crud_f, db_session):
    """
    Негативный тест ф-ций manage_users_involved и manage_places.
    Случай когда strike_id переданный с фронта отсутствует.
    """
    with pytest.raises(ModelEntryDoesNotExistsInDbError, match=f'Strike with id 1 does not exists'):
        await crud_f(db_session, 1, object)


async def test_get_strikes(strike_factory, db_session):
    """


    """
    strikes = strike_factory.build_batch(size=2, num_group=2)
    db_session.add_all(strikes)
    await db_session.commit()

    res = await get_strikes(db_session, [], params, only_active=False)

    strikes_from_db = res.items

    for strike in strikes_from_db:
        assert strike.union is not None
        assert strike.enterprise is not None
        # assert strike.group_ids_from_exp == await strike.awaitable_attrs.group_ids_ap


