import asyncio

from internal.database import async_session
from models import DetentionMaterializedView
from loguru import logger

__all__ = (
    'Scheduler',
)


class Scheduler:
    """
    Запускает задачи асинхронно с определенным интервалом.
    """
    timeout: float = 0.0
    name: str
    __tasks__ = {}

    @classmethod
    def run(cls) -> None:
        """
        Запуск всех задач.
        """
        for sub_cls in cls.__subclasses__():
            cls.__tasks__[sub_cls.name] = asyncio.create_task(sub_cls.wrapped_task())

    @classmethod
    def stop(cls) -> None:
        """
        Остановка всех задач.
        """
        for name, task in cls.__tasks__.items():
            msg = f'Task {name} canceled forcibly.'
            task.cancel(msg)
            logger.info(msg)

    @classmethod
    async def task(cls) -> None:
        """
        Одна задача для выполнения.
        """
        raise NotImplementedError()

    @classmethod
    async def wrapped_task(cls) -> None:
        """
        Задача для выполнения обернутая в блок try/except с логированием и
        выполняемая в бесконечном цикле через определенный временной интервал.
        """
        while True:
            try:
                await cls.task()
            except Exception as err:
                logger.exception(str(err))
            else:
                logger.info(f'Task {cls.name} has finished successfully!')

            await asyncio.sleep(cls.timeout)


class DetentionMaterializedViewRefresher(Scheduler):
    """
    Обновление представления DetentionMaterializedView раз в час.
    """
    timeout = DetentionMaterializedView._refresh_period
    name = f'Refresh {DetentionMaterializedView.__name__} view'

    @classmethod
    async def task(cls):
        async with async_session() as session:
            await DetentionMaterializedView.refresh(session, concurrently=False)
            await session.commit()
