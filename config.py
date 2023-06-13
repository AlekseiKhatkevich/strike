import datetime
from functools import cache
from pathlib import Path

from pydantic import (
    BaseSettings,
    RedisDsn,
    PostgresDsn,
    SecretStr,
    FilePath,
)

__all__ = (
    'settings',
    'get_settings',
    'Settings',
)


class Settings(BaseSettings):
    """
    Базовые настройки проекта.
    """
    pg_dsn: PostgresDsn
    pg_dsn_direct: PostgresDsn
    redis_dsn: RedisDsn
    secret_string: SecretStr
    debug: bool = False
    root_path: Path = Path(__file__).resolve().parent
    logging_config_file_path: FilePath = 'internal/logging/configuration.yaml'
    access_token_expire_minutes: int
    obtain_jwt_token_ratelimit: str = '10/minute'
    user_cache_persistence: datetime.timedelta = datetime.timedelta(minutes=60)
    redis_socket_connection_timeout: float
    redis_socket_timeout: float

    class Config:
        env_file = '.env'


@cache
def get_settings() -> Settings:
    """
    Отдает базовые настройки проекта.
    :return: Settings
    """
    return Settings()


settings: Settings = get_settings()
