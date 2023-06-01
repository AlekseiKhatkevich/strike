import bcrypt

from internal.constants import HASH_ENCODING

__all__ = (
    'make_hash',
    'verify_hash',
)


def make_hash(raw_value: str) -> str:
    """
    Создает хаш.
    """
    bytes_value = raw_value.encode(HASH_ENCODING)
    salt = bcrypt.gensalt()
    value_hash = bcrypt.hashpw(bytes_value, salt)
    return value_hash.decode(HASH_ENCODING)


def verify_hash(raw_value: str, _hash: str) -> bool:
    """
    Валидирует хаш.
    """
    return bcrypt.checkpw(
        raw_value.encode(HASH_ENCODING),
        _hash.encode(HASH_ENCODING),
    )
