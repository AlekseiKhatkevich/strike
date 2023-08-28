import asyncio
from collections import defaultdict
import orjson
from aiokafka import AIOKafkaConsumer
from loguru import logger
from shapely import LineString

from serializers.for_kafka import KafkaCoordinatesDeSerializer


conf = dict(
    bootstrap_servers='127.0.0.1:29092',
    group_id='coordinates_consumers1',
    enable_auto_commit=True,
    auto_commit_interval_ms=0.3 * 1000,
    auto_offset_reset='earliest',
    metadata_max_age_ms=10 * 1000,
    # isolation_level='read_committed'
)


class CoordinatesStorage:
    """

    """

    def __init__(self, save_window, save_len):
        self.save_window = save_window
        self.save_len = save_len
        self._storage = defaultdict(list)

    def add(self, ser):
        self._storage[ser.user_id].append(ser)

    def _do_save(self, coords, user_id):
        route = LineString(c.point for c in coords)
        logger.info(f'Line {route} saved for user {user_id}')
        self._storage[user_id].clear()

    def save(self, user_id, force=False):
        coords = self._storage[user_id]
        if len(coords) < 2:
            return None
        if force:
            return self._do_save(coords, user_id=user_id)
        *_, penultimate, ultimate = coords
        if (ultimate._timestamp - penultimate._timestamp > self.save_window or
                len(coords) >= self.save_len):
            return self._do_save(coords, user_id=user_id)


class KafkaCoordinatesConsumer:
    """
    """

    def __init__(self, cons_qty, poll_delay=1, save_window=60 * 1000, save_len=100):
        self.cons_qty = cons_qty
        self.poll_delay = poll_delay
        self.cons_user_id_map = defaultdict(set)
        self.storage = CoordinatesStorage(save_window, save_len)

    def _handle_one_coord(self, msg):
        data = orjson.loads(msg.value)
        ser = KafkaCoordinatesDeSerializer(timestamp=msg.timestamp, **data)
        self.storage.add(ser)
        self.storage.save(ser.user_id, force=False)

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
                self._handle_one_coord(msg)
        finally:
            await consumer.stop()
            logger.info(f'Consumer # {number} has stopped')

    async def consume(self):
        coros = []
        for num in range(self.cons_qty):
            consumer = AIOKafkaConsumer(
                'coordinates',
                **conf,
            )
            coro = self._one_consumer(num, consumer)
            coros.append(coro)

        await asyncio.gather(*coros)
