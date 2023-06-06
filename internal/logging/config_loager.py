from logging.config import dictConfig

import yaml

from internal.constants import LOGGING_CONFIG_FILE_PATH

__all__ = (
    'load_yaml_logging_config',
    'configure_loggers',
)


def load_yaml_logging_config() -> dict:
    """
    Загружает конфиг для логирования из yaml файла.
    """
    with open(LOGGING_CONFIG_FILE_PATH, 'r') as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    return config


def configure_loggers() -> None:
    """
    Конфигурирует логер конфигом из yaml файла.
    """
    dictConfig(load_yaml_logging_config())
