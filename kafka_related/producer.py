import asyncio
import contextlib
import heapq
import random
from itertools import count
from typing import AsyncIterator, Iterable
import aiorun
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient
from confluent_kafka.cimpl import KafkaException, NewPartitions, NewTopic
from loguru import logger
from shapely import Point
from shapely.geometry import LineString

from serializers.for_kafka import KafkaCoordinatesSerializer

partitions_lock = asyncio.Lock()

config = {
    'bootstrap.servers': '127.0.0.1:29092',
    'client.id': 228,
}


coordinates_topic = NewTopic(
    'coordinates',
    num_partitions=10,
    config={
       'delete.retention.ms': 604800000,
    }
)


class KafkaPointsProducer:
    """
    Пишет координаты юзера по ходу его маршрута в Кафку.
    """
    def __init__(self, num_users: int | None = None, topic: NewTopic = coordinates_topic) -> None:
        self.producer = Producer(config)
        self.admin = AdminClient(config)
        self.topic = topic
        self.known_user_ids = {}
        self.used_partitions_counter = count()
        num_users = num_users or random.randint(50, 100)
        self.routes = [
            RandomRoute(*self.generate_random_start_and_stop(), user_id=num) for num in range(1, num_users)
        ]
        self._configure()

    def _configure(self) -> None:
        """
        Начальная конфигурация брокера и топика.
        1) Создаем топик с 10ю начальными партициями.
        """
        self.admin.create_topics([self.topic], request_timeout=0.05)

    @property
    def _partitions_count(self) -> int:
        """
        Кол-во партиций топика на текущий момент времени.
        """
        return len(self.producer.list_topics().topics[self.topic.topic].partitions)

    @staticmethod
    def generate_random_start_and_stop() -> tuple[Point, Point]:
        """
        Рандомные точки начала и окончания маршрута.
        """
        start_lat = random.uniform(-90, 90)
        start_lon = random.uniform(-180, 180)
        end_lat = random.uniform(start_lat - 0.01, start_lat + 0.01)
        end_lon = random.uniform(start_lon - 0.01, start_lon + 0.01)

        return Point(start_lon, start_lat), Point(end_lon, end_lat)

    async def _send_one_event(self, route: 'RandomRoute') -> None:
        """
        Отправляет 1 эвент с координатами юзера на Кафку.
        """
        async for point in route.produce_points():
            if route.user_id not in self.known_user_ids:
                #  Присваиваем конкретному user_id свой partition_id
                self.known_user_ids[route.user_id] = next(self.used_partitions_counter)
                async with partitions_lock:
                    resp = self.admin.create_partitions(
                        [NewPartitions(self.topic.topic, len(self.known_user_ids) + 3)],
                        request_timeout=0.05,
                    )
                    # Ждем пока создастся партиция перед тем как продолжить
                    # KafkaException - если партиция уже существует - но нам это ок
                    with contextlib.suppress(KafkaException, TimeoutError):
                        resp[self.topic.topic].result(0.5)
            if point:
                data_serializer = KafkaCoordinatesSerializer(user_id=route.user_id, point=point)
                self.producer.produce(
                    topic=self.topic.topic,
                    key=str(route.user_id),
                    value=data_serializer.model_dump_json(),
                    partition=self.known_user_ids[route.user_id],
                )
                logger.info(
                    f'User_id = {route.user_id}, point = {point}, partition = {self.known_user_ids[route.user_id]}'
                )

    async def produce(self) -> None:
        """
        Запускаем всю процедуру.
        """
        self.producer.poll(0)
        await asyncio.gather(*(self._send_one_event(route) for route in self.routes))
        logger.info('Done!')


class OriginDistanceHeap:
    """
    Куча, которая хранит набор точек (Shapely Point) отсортированными по дальности
    от какой-то начальной точки.
    """
    def __init__(self, random_points: Iterable[Point], *, first_point: Point) -> None:
        self.heap = [
            (first_point.distance(p), p) for p in random_points
        ]
        heapq.heapify(self.heap)

    def pop(self) -> tuple[float, Point]:
        """
        POP() одного элемента из кучи самого близкого к первоначальной точке.
        """
        return heapq.heappop(self.heap)

    @property
    def is_empty(self):
        """
        Есть ли в куче элементы еше.
        """
        return not bool(self.heap)


class RandomRoute:
    """
    Генерирует рандомный маршрут из последовательных точек.
    """
    def __init__(self,
                 first_point: Point,
                 last_point: Point,
                 *,
                 user_id: int,
                 num_points: int | None = None,
                 ):
        self.first_point = first_point
        self.last_point = last_point
        self.user_id = user_id

        num_points = num_points or random.randint(10, 1000)
        random_points = self._produce_random_points(num_points)
        self.heap = OriginDistanceHeap(random_points, first_point=first_point)

    def _produce_random_points(self, num_points: int) -> list[Point, ...]:
        """
        Создает НЕ ОТСОРТИРОВАННЫЙ по удалению от первоначальной точки набор точек пути
        вдоль линии соединяющей первую и последнюю точку маршрута.
        """
        line = LineString([self.first_point, self.last_point])

        intermediate_points = []
        for _ in range(num_points):
            point = line.interpolate(random.random(), True)
            intermediate_points.append(point)

        return intermediate_points

    async def produce_points(self) -> AsyncIterator[Point]:
        """
        Отдает точки маршрута последовательно начиная от начальной точки, затем спит
        от 0,5 до 3 секунд.
        """
        while not self.heap.is_empty:
            _, point = self.heap.pop()
            yield point
            await asyncio.sleep(random.uniform(0.5, 3))


if __name__ == '__main__':
    aiorun.run(KafkaPointsProducer(num_users=10).produce())
