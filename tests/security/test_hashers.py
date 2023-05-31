import re

import pytest

from internal.constants import BCRYPT_REGEXP
from security.hashers import make_hash, verify_hash

initial_password = 'super_secret_password'


@pytest.fixture(scope='module')
def hashed() -> str:
    """
    Хэшированный с помощью BCRYPT пароль.
    """
    return make_hash(initial_password)


def test_make_hash_positive(hashed):
    """
    Пробуем хэшировать пароль.
    """
    assert re.match(BCRYPT_REGEXP, hashed)


def test_verify_hash_positive(hashed):
    """
    Сравниваем полученный хеш пароля с ним самим.
    """
    assert verify_hash(initial_password, hashed)
