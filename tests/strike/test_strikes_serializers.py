import pytest

from models import UserRole
from serializers.enterprises import EnterpriseInSerializer
from serializers.places import PlaceInSerializer
from serializers.strikes import (
    AddRemoveStrikeM2MObjectsSerializer,
    AddRemoveUsersInvolvedSerializer,
    StrikeInSerializer,
    StrikeOutSerializerFull,
    UsersInvolvedInSerializer,
    UsersInvolvedOutSerializer,
)


@pytest.fixture
def base_positive_input_data(faker):
    """
    Позитивные данные получаемые на вход сериалайзером StrikeInSerializer.
    """
    return dict(
        duration=['2023-07-09T09:40:40.928935+00:00', '2023-07-10T09:40:40.928935+00:00'],
        planned_on_date=faker.date(),
        goals='test goals',
        results='test_results',
        overall_num_of_employees_involved=faker.pyint(min_value=100),
        union_in_charge_id=faker.pyint(min_value=1),
        enterprise=faker.pyint(min_value=1),
        group=None,
        places=None,
        users_involved=None,
    )


def test_StrikeInSerializer_positive(base_positive_input_data):
    """
    Позитивный тест сериалайзера StrikeInSerializer.
    """
    StrikeInSerializer(**base_positive_input_data)


def test_StrikeInSerializer_positive_new_enterprise(base_positive_input_data, enterprise_factory):
    """
    Позитивный тест сериалайзера StrikeInSerializer. Случай, когда enterprise
    передается как набор полей, а не id: int.
    """
    enterprise = enterprise_factory.build()
    base_positive_input_data['enterprise'] = enterprise.__dict__

    ser = StrikeInSerializer(**base_positive_input_data)

    assert isinstance(ser.enterprise, EnterpriseInSerializer)
    assert set(ser.enterprise.model_dump(exclude={'id', }).items()) <= set(enterprise.__dict__.items())


def test_StrikeInSerializer_positive_with_group(base_positive_input_data):
    """
    Позитивный тест сериалайзера StrikeInSerializer. Случай с передачей группы.
    """
    base_positive_input_data['group'] = list(range(1, 6))

    ser = StrikeInSerializer(**base_positive_input_data)

    assert ser.group == list(range(1, 6))


def test_StrikeInSerializer_positive_new_places(base_positive_input_data, place_factory):
    """
    Позитивный тест сериалайзера StrikeInSerializer. Случай с передачей данный Place как
    смесь из id: int и вложенных PlaceInSerializer.
    """
    places = place_factory.build_batch(size=3)
    base_positive_input_data['places'] = []
    for place in places:
        place_data = {
            'name': place.name,
            'address': place.address,
            'coordinates': place.coords_in_decimal,
        }
        base_positive_input_data['places'].append(place_data)

    base_positive_input_data['places'].extend([1, 2, 3])

    ser = StrikeInSerializer(**base_positive_input_data)

    for place in ser.places:
        assert isinstance(place, PlaceInSerializer | int)


def test_StrikeInSerializer_positive_with_users_involved(base_positive_input_data, faker):
    """
    Позитивный тест сериалайзера StrikeInSerializer. Случай с передачей набора id:int вовлеченных
    юзеров.
    """
    users_involved = [
        {'user_id': str(_id), 'role': faker.enum(UserRole).value.lower()} for _id in range(1, 6)
    ]
    base_positive_input_data['users_involved'] = users_involved

    ser = StrikeInSerializer(**base_positive_input_data)

    for ui in ser.users_involved:
        assert isinstance(ui, UsersInvolvedInSerializer)
        assert ui.role.value.isupper()


def test_StrikeInSerializer_negative_both_dates_are_none(base_positive_input_data):
    """
    Негативный тест сериалайзера StrikeInSerializer.
    planned_on_date и duration не могут быть None одновременно.
    """
    base_positive_input_data |= {'planned_on_date': None, 'duration': None}
    expected_error_message = 'Please specify either "planned_on_date" or "duration" field.'

    with pytest.raises(ValueError, match=expected_error_message):
        StrikeInSerializer(**base_positive_input_data)


def test_StrikeOutSerializer_positive(strike):
    """
    Позитивный тест сериалайзера StrikeOutSerializer отдачи данных Strike на фронт.
    """
    strike.group_ids = list(range(1, 6))
    strike.users_involved_ids = list(range(1, 6))
    strike.places_ids_list = list(range(1, 6))

    ser = StrikeOutSerializerFull.model_validate(strike)

    assert ser.id == strike.id
    assert ser.enterprise_id == strike.enterprise_id
    assert ser.group_ids == strike.group_ids
    assert ser.created_by_id == strike.created_by_id
    assert ser.users_involved_ids == strike.users_involved_ids
    assert ser.places_ids == strike.places_ids_list


def test_UsersInvolvedOutSerializer(strike_to_user_association_factory):
    """
    Позитивный тест сериалайзера UsersInvolvedOutSerializer.
    """
    intermediate_model = strike_to_user_association_factory.build(user_id=1)
    UsersInvolvedOutSerializer.model_validate(intermediate_model)


@pytest.mark.parametrize(
    'add, remove',
    [({1, 2, 3}, {4, 5}), ({1, 2}, set()), (set(), {1, 2}), (set(), set())]
)
def test_AddRemoveStrikeM2MObjectsSerializer_positive(add, remove):
    """
    Позитивный тест сериалайзера AddRemoveStrikeM2MObjectsSerializer.
    """
    AddRemoveStrikeM2MObjectsSerializer(add=add, remove=remove)


def test_AddRemoveStrikeM2MObjectsSerializer_negative():
    """
    Негативный тест сериалайзера AddRemoveStrikeM2MObjectsSerializer. Id из add и remove
    не должны пересекаться.
    """
    with pytest.raises(ValueError):
        AddRemoveStrikeM2MObjectsSerializer(add={1, }, remove={1, })


def test_AddRemoveUsersInvolvedSerializer_positive(faker):
    """
    Позитивный тест сериалайзера AddRemoveUsersInvolvedSerializer.
    """
    add = [
        dict(user_id=user_id, role=faker.random_element(elements=list(UserRole)).value)
        for user_id in range(1, 4)
    ]
    remove = {10, 11, 12}

    AddRemoveUsersInvolvedSerializer(add=add, remove=remove)


def test_AddRemoveUsersInvolvedSerializer_negative(faker):
    """
    Негативный тест сериалайзера AddRemoveUsersInvolvedSerializer. user_id из add и remove
    не должны пересекаться.
    """
    with pytest.raises(ValueError):
        AddRemoveUsersInvolvedSerializer(
            add=[dict(user_id=1, role=faker.random_element(elements=list(UserRole)).value)],
            remove={1, }
        )
