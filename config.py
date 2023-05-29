from functools import cache

from pydantic import (
    BaseSettings,
    RedisDsn,
    PostgresDsn,
    SecretStr,
)


__all__ = (
    'settings',
    'get_settings',
)


class Settings(BaseSettings):
    """
    Базовые настройки проекта.
    """
    pg_dsn: PostgresDsn
    pg_dsn_direct: PostgresDsn
    redis_dsn: RedisDsn
    secret_string: SecretStr


@cache
def get_settings() -> Settings:
    """
    Отдает базовые настройки проекта.
    :return: Settings
    """
    return Settings()


settings: Settings = get_settings()
