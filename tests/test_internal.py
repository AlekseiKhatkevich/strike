import pytest

from internal.database import Base
from models import User


@pytest.mark.parametrize(
    'name, model',
    [
        ('User', User),
        pytest.param('HuiUser', None, marks=pytest.mark.xfail(
            raises=LookupError,
            strict=True,
        ))
    ]
)
def test_get_model_by_name(name, model):
    """
    Метод должен вернуть модель по ее имени или возбудить исключение если
    модель не была найдена.
    """
    assert Base.get_model_by_name(name) == model
