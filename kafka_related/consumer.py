import asyncio
from collections import defaultdict
import orjson
from aiokafka import AIOKafkaConsumer
from loguru import logger

from serializers.for_kafka import KafkaCoordinatesDeSerializer

# conf = {
#     'bootstrap.servers': '127.0.0.1:29092',
#     'group.id': 'coordinates_consumers1',
#     'auto.offset.reset': 'earliest',
#     'enable.auto.commit': True,
#     'heartbeat.interval.ms': 3000,
# }
aioconf = dict(
    bootstrap_servers='127.0.0.1:29092',
    group_id='coordinates_consumers1',
    enable_auto_commit=True,
    auto_commit_interval_ms=100,
    auto_offset_reset='earliest',
)


class CoordinatesStorage:
    """

    """
    def __init__(self):
        self._storage = defaultdict(list)

    def add(self, user_id, ser):


class KafkaCoordinatesConsumer:
    """
    """
    def __init__(self, cons_qty, poll_delay=1):
        self.cons_qty = cons_qty
        self.poll_delay = poll_delay
        self.cons_user_id_map = defaultdict(set)
        self.storage = CoordinatesStorage()

    def _handle_one_coord(self, msg):
        data = orjson.loads(msg.value)
        ser = KafkaCoordinatesDeSerializer(**data)
        self.storage

    async def _one_consumer(self, number, consumer):
        logger.info(f'Starting consumer # {number}')
        await consumer.start()
        try:
            async for msg in consumer:
                logger.info(
                    f'Consumer # {number},'
                    f' partition # {msg.partition},'
                    f' key # {msg.key},'
                    f' offset # {msg.offset},'
                    f' value - {msg.value}'
                )
                self.cons_user_id_map[number].add(msg.key)
        finally:
            await consumer.stop()
            logger.info(f'Consumer # {number} has stopped')

    async def consume(self):
        coros = []
        for num in range(self.cons_qty):
            consumer = AIOKafkaConsumer(
                'coordinates',
                **aioconf,
            )
            coro = self._one_consumer(num, consumer)
            coros.append(coro)

        await asyncio.gather(*coros)
