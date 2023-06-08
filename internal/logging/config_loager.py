import yaml
from loguru import logger

from config import settings

__all__ = (
    'load_yaml_logging_config',
    'configure_loggers',
)


def load_yaml_logging_config() -> dict:
    """
    Загружает конфиг для логирования из yaml файла.
    """
    with open(settings.logging_config_file_path, 'r') as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    return config


def configure_loggers() -> None:
    """
    Конфигурирует логер конфигом из yaml файла.
    """
    # dictConfig(load_yaml_logging_config())
    logger.add('logs/warn+.log', rotation='10 MB', level='WARNING', enqueue=True)

