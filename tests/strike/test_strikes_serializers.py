import datetime

import pytest
from sqlalchemy.dialects.postgresql import Range

from internal.serializers import BaseModel
from models import UserRole
from serializers.enterprises import EnterpriseInSerializer
from serializers.places import PlaceInSerializer
from serializers.strikes import (
    DatetimeRangeField,
    StrikeInSerializer,
    StrikeOutSerializer,
    UsersInvolvedInSerializer,
)


@pytest.fixture(scope='module')
def test_serializer() -> 'TestSerializer':
    class TestSerializer(BaseModel):
        dt_range: DatetimeRangeField

    return TestSerializer


@pytest.mark.parametrize(
    'input_lower, input_upper',
    [
        ('2023-07-09T09:40:40.928935+00:00', '2023-07-10T09:40:40.928935+00:00',),
        (None, '2023-07-10T09:40:40.928935+00:00',),
        ('2023-07-09T09:40:40.928935+00:00', None,),
    ]
)
def test_DatetimeRangeField_positive_input(input_lower, input_upper, test_serializer):
    """
    Позитивный тест сериалайзера DatetimeRangeField.
    """
    ser = test_serializer(dt_range=[input_lower, input_upper])

    assert isinstance(ser.dt_range, Range)

    if input_lower is not None:
        input_lower_deserialized = datetime.datetime.fromisoformat(input_lower)
        assert ser.dt_range.lower == input_lower_deserialized
    else:
        assert input_lower is None

    if input_upper is not None:
        input_upper_deserialized = datetime.datetime.fromisoformat(input_upper)
        assert ser.dt_range.upper == input_upper_deserialized
    else:
        assert input_upper is None


@pytest.mark.parametrize(
    'input_lower, input_upper, message',
    [
        ('2023-07-09T09:40:40.928935', '2023-07-10T09:40:40.928935+00:00', 'Only aware datetime are accepted'),
        ('2023-07-10T09:40:40.928935+00:00', '2023-07-09T09:40:40.928935+00:00',
         'Second datetime in range should be greater then first one.'),
        (None, None, 'Please specify at leas one datetime in range.')
    ]
)
def test_DatetimeRangeField_negative_input(input_lower, input_upper, message, test_serializer):
    """
    Негативный тест сериалайзера DatetimeRangeField.
    """
    with pytest.raises(ValueError, match=message):
        test_serializer(dt_range=[input_lower, input_upper])


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
    assert set(ser.enterprise.dict(exclude={'id', }).items()) <= set(enterprise.__dict__.items())


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

    ser = StrikeOutSerializer.from_orm(strike)

    assert ser.id == strike.id
    assert ser.enterprise_id == strike.enterprise_id
    assert ser.group_ids == strike.group_ids
    assert ser.created_by_id == strike.created_by_id
    assert ser.users_involved_ids == strike.users_involved_ids
    assert ser.places_ids == strike.places_ids_list
