import functools
import operator
from numbers import Number
from typing import TypeVar

__all__ = (
    'positive_integer_only',
    'limit_value_validator',
)


NUMBER_T = TypeVar('NUMBER_T', bound=Number)


def limit_value_validator(field_name: str,
                          value: NUMBER_T,
                          limit: Number,
                          condition_f: callable,
                          error_message: str | None = None,
                          ) -> NUMBER_T:
    """
    :param error_message: Не обязательный текст исключения.
    :param field_name: Название поля модели.
    :param value: Само валидируемое значение (int, float, decimal и др.)
    :param limit: Граница больше или меньше которой должно быть значение.
    :param condition_f: Ф-ция которая должна принимать value и limit и отдавать True
    в случае если все ОК и False если значение нарушает условие. В основном это operator
    gt, ge, lt, le ...
    :return: value
    """
    default_error_message = f"{field_name} field's value {value} is out of range {limit}."

    error_message = error_message.format(**locals()) if error_message is not None else default_error_message
    if not condition_f(value, limit):
        raise ValueError(error_message)
    else:
        return value


positive_integer_only = functools.partial(limit_value_validator, limit=1, condition_f=operator.ge)
