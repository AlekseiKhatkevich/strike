import asyncio

from internal.database import async_session
from models import DetentionMaterializedView
from loguru import logger

__all__ = (
    'Scheduler',
)


class Scheduler:
    """

    """
    timeout: float = 0.0
    name: str
    __tasks__ = {}

    @classmethod
    def run(cls):
        for sub_cls in cls.__subclasses__():
            cls.__tasks__[sub_cls.name] = asyncio.create_task(sub_cls.wrapped_task())

    @classmethod
    def stop(cls):
        for name, task in cls.__tasks__.items():
            msg = f'Task {name} canceled forcibly.'
            task.cancel(msg)
            logger.info(msg)

    @classmethod
    async def task(cls):
        pass

    @classmethod
    async def wrapped_task(cls):
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

    """
    timeout = 5.0
    name = f'Refresh {DetentionMaterializedView.__name__} view.'

    @classmethod
    async def task(cls):
        async with async_session() as session:
            await DetentionMaterializedView.refresh(session, concurrently=False)
