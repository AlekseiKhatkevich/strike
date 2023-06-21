import operator

import pytest

from models.validators import limit_value_validator


def test_limit_value_validator_positive():
    """
    Позитивный тест валидатора limit_value_validator. Если условие соблюдается - то исключение
    не должно быть вызвано.
    """
    limit_value_validator(
        field_name='test_field_name',
        limit=10,
        condition_f=operator.ge,
        value=11,
    )


@pytest.mark.parametrize('expected_error_message, error_message', [
    ("{field_name} field's value {value} is out of range {limit}.", False),
    ("Field {field_name} should have value > {limit}, but in fact it has {value}", True),
])
def test_limit_value_validator_negative(expected_error_message, error_message):
    """
    Негативный тест валидатора limit_value_validator. Если условие не соблюдается - то исключение
    будет вызвано.
    """
    kwargs = dict(
        field_name='test_field_name',
        value=9,
        limit=10,
        condition_f=operator.ge,
    )
    if error_message:
        kwargs['error_message'] = expected_error_message

    with pytest.raises(ValueError, match=expected_error_message.format(**kwargs)):
        limit_value_validator(
            **kwargs
        )
