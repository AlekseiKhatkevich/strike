from numbers import Number
from typing import TypeVar


__all__ = (
    'limit_value_validator',
)


NUMBER_T = TypeVar('NUMBER_T', bound=Number)


def limit_value_validator(field_name: str,
                          value: NUMBER_T,
                          limit: Number,
                          condition_f: callable,
                          ) -> NUMBER_T:
    """
    :param field_name: Название поля модели.
    :param value: Само валидируемое значение (int, float, decimal и др.)
    :param limit: Граница больше или меньше которой должно быть значение.
    :param condition_f: Ф-ция которая должна принимать value и limit и отдавать True
    в случае если все ОК и False если значение нарушает условие. В основном это operator
    gt, ge, lt, le ...
    :return: value
    """
    if not condition_f(value, limit):
        raise ValueError(
            f"{field_name} field's value {value} is out of range {limit}."
        )
    else:
        return value
