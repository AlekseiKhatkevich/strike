import datetime
from functools import cache
from pathlib import Path

from pydantic import (
    ConfigDict, FilePath,
    PostgresDsn,
    RedisDsn,
    SecretStr,
)
from pydantic_settings import BaseSettings

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
    # logging_config_file_path: FilePath = 'internal/logging/configuration.yaml'
    access_token_expire_minutes: int = 10000000
    obtain_jwt_token_ratelimit: str = '10/minute'
    user_cache_persistence: datetime.timedelta = datetime.timedelta(minutes=60)
    redis_socket_connection_timeout: float = 0.5
    redis_socket_timeout: float = 0.5
    grpc_port: str

    model_config = ConfigDict(extra='ignore')


@cache
def get_settings() -> Settings:
    """
    Отдает базовые настройки проекта.
    :return: Settings
    """
    return Settings()


settings: Settings = get_settings()
