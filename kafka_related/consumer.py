import asyncio
import datetime
import enum
from collections import defaultdict
import orjson
from aiokafka import AIOKafkaConsumer, TopicPartition
from loguru import logger
from shapely import LineString

from crud.kafka import CoorsPreparer, save_route_into_db
from internal.database import async_session
from serializers.for_kafka import KafkaCoordinatesDeSerializer

kafka_conf = dict(
    bootstrap_servers='127.0.0.1:29092',
    group_id='coordinates_consumers1',
    enable_auto_commit=False,
    auto_commit_interval_ms=0.3 * 1000,
    auto_offset_reset='earliest',
    metadata_max_age_ms=10 * 1000,
    # isolation_level='read_committed'
)
storage_conf = dict(
    save_window=60 * 1000,
    save_len=100,
)

stop_event = asyncio.Event()


class SaveType(enum.Enum):
    """

    """
    WITHOUT_SAVE = 0
    WITH_ROUTE_SPLIT = 1
    WITHOUT_ROUTE_SPLIT = 2


class CoordinatesStorage:
    """

    """

    def __init__(self, save_window, save_len):
        self.save_window = save_window
        self.save_len = save_len
        self._storage = defaultdict(list)

    async def add(self, ser, *, save_if_needed):
        self._storage[ser.user_id].append(ser)
        if save_if_needed:
            return await self.save(user_id=ser.user_id)
        return SaveType.WITHOUT_SAVE

    @staticmethod
    async def _do_save(coords, user_id):
        async with async_session() as session:
            preparer = CoorsPreparer(user_id, coords)
            return await save_route_into_db(session, preparer.data_for_saving)

    async def save(self, user_id, by_timer=False):
        coords = self._storage[user_id]

        if len(coords) < 2:
            return SaveType.WITHOUT_SAVE

        *rest_coords, penultimate, ultimate = coords
        time_diff = ultimate._timestamp - penultimate._timestamp
        #  Пришла точка с разницей во времени по отношению к предыдущей >= save_window (60 сек)
        #  Значит эта точка - это первая точка начала НОВОГО маршрута, а старый нужно сохранить.
        if time_diff >= self.save_window:
            # Последняя координата будет являться первой координатой нового маршрута.
            # Ее не сохраняем здесь, а потом в новом маршруте.
            if rest_coords:  # нужно хотя бы 2 точки для сохранения маршрута.
                await self._do_save([*rest_coords, penultimate], user_id=user_id)
            #  Удаляем все кроме последней точки
            self._storage[user_id] = [ultimate]
            return SaveType.WITH_ROUTE_SPLIT

        #  Если кол-во точек >= save_len (100 штук)
        elif len(coords) >= self.save_len or (by_timer and self._timer_condition(ultimate)) :
            await self._do_save(coords, user_id=user_id)
            self._storage[user_id].clear()
            return SaveType.WITHOUT_ROUTE_SPLIT
        else:
            return SaveType.WITHOUT_SAVE

    def _timer_condition(self, ultimate):
        return ((ultimate._process_time + self.save_window) <
                (datetime.datetime.now(tz=datetime.UTC).timestamp() * 1000))

    async def save_on_timer(self):
        for user_id in self._storage.keys():
            yield await self.save(user_id, by_timer=True)


class SingleConsumer:
    def __init__(self, num):
        self.storage = CoordinatesStorage(**storage_conf)
        self.num = num
        self.kafka_consumer = AIOKafkaConsumer('coordinates', **kafka_conf)

    async def save_all(self):
        async for save_type in self.storage.save_on_timer():
            if save_type != SaveType.WITHOUT_SAVE:
                await self.kafka_consumer.commit()

    async def consume_forever(self):
        # noinspection PyProtectedMember
        logger.info(f'Starting consumer # {self.num}')
        await self.kafka_consumer.start()
        try:
            async for msg in self.kafka_consumer:
                logger.info(
                    f'Consumer # {self.num},'
                    f' partition # {msg.partition},'
                    f' key # {msg.key},'
                    f' offset # {msg.offset},'
                    f' value - {msg.value}'
                )
                save_type = await self._handle_one_coord(msg)
                await self._handle_commit(msg, save_type)
                if stop_event.is_set():
                    raise SystemExit(0)
        finally:
            await self.kafka_consumer.stop()
            logger.info(f'Consumer # {self.num} has stopped')

    async def _handle_commit(self, msg, save_type):
        match save_type:
            case SaveType.WITHOUT_SAVE:
                return None
            case SaveType.WITHOUT_ROUTE_SPLIT:
                await self.kafka_consumer.commit()
                logger.info(f'Consumer # {self.num} committed offset # {msg.offset + 1}')
            case SaveType.WITH_ROUTE_SPLIT:
                tp = TopicPartition(msg.topic, msg.partition)
                await self.kafka_consumer.commit({tp: msg.offset})
                logger.info(f'Consumer # {self.num} committed offset # {msg.offset}')

    async def _handle_one_coord(self, msg):
        data = orjson.loads(msg.value)
        ser = KafkaCoordinatesDeSerializer(timestamp=msg.timestamp, **data)
        return await self.storage.add(ser, save_if_needed=True)


class KafkaCoordinatesConsumer:
    """
    """

    def __init__(self, cons_qty, schedule_saver_period=10.0):
        self.cons_qty = cons_qty
        self.schedule_saver_period = schedule_saver_period
        self.consumers = [SingleConsumer(num) for num in range(self.cons_qty)]

    async def consume(self):
        coros = [consumer.consume_forever() for consumer in self.consumers]
        await asyncio.gather(*coros, self.save_on_schedule())

    async def save_on_schedule(self):
        while not stop_event.is_set():
            await asyncio.sleep(self.schedule_saver_period)
            for consumer in self.consumers:
                logger.info(f'Initiate save on timer for consumer # {consumer.num}')
                await consumer.save_all()
