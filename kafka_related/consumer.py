import asyncio
from collections import defaultdict
import orjson
from aiokafka import AIOKafkaConsumer
from loguru import logger
from shapely import LineString

from serializers.for_kafka import KafkaCoordinatesDeSerializer


kafka_conf = dict(
    bootstrap_servers='127.0.0.1:29092',
    group_id='coordinates_consumers1',
    enable_auto_commit=True,
    auto_commit_interval_ms=0.3 * 1000,
    auto_offset_reset='earliest',
    metadata_max_age_ms=10 * 1000,
    # isolation_level='read_committed'
)
storage_conf = dict(
    save_window=60 * 1000,
    save_len=100,
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


class SingleConsumer:
    def __init__(self, num):
        self.storage = CoordinatesStorage(**storage_conf)
        self.kafka_consumer = AIOKafkaConsumer('coordinates', client_id=num, **kafka_conf)

    async def consume_forever(self):
        # noinspection PyProtectedMember
        client_id = self.kafka_consumer._client._client_id
        logger.info(f'Starting consumer # {client_id}')
        await self.kafka_consumer.start()
        try:
            async for msg in self.kafka_consumer:
                logger.info(
                    f'Consumer # {client_id},'
                    f' partition # {msg.partition},'
                    f' key # {msg.key},'
                    f' offset # {msg.offset},'
                    f' value - {msg.value}'
                )
                self._handle_one_coord(msg)
        finally:
            await self.kafka_consumer.stop()
            logger.info(f'Consumer # {client_id} has stopped')

    def _handle_one_coord(self, msg):
        data = orjson.loads(msg.value)
        ser = KafkaCoordinatesDeSerializer(timestamp=msg.timestamp, **data)
        self.storage.add(ser)
        # self.storage.save(ser.user_id, force=False)


class KafkaCoordinatesConsumer:
    """
    """

    def __init__(self, cons_qty):
        self.cons_qty = cons_qty
        self.consumers = [SingleConsumer(num) for num in range(self.cons_qty)]

    async def consume(self):
        coros = [consumer.consume_forever() for consumer in self.consumers]
        await asyncio.gather(*coros)
