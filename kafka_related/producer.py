import asyncio
import heapq
import random

from confluent_kafka import Producer
from shapely import Point
from shapely.geometry import LineString

config = {
    'bootstrap.servers': '127.0.0.1:29092',
}


class KafkaPointsProducer:
    def __init__(self, num_users=None):
        self.producer = Producer(config)
        num_users = num_users or random.randint(50, 100)
        self.routes = [
            RandomRoute(*self.generate_random_start_and_stop(), user_id=num) for num in range(1, num_users)
        ]

    @staticmethod
    def generate_random_start_and_stop():
        start_lat = random.uniform(-90, 90)
        start_lon = random.uniform(-180, 180)
        end_lat = random.uniform(start_lat - 0.01, start_lat + 0.01)
        end_lon = random.uniform(start_lon - 0.01, start_lon + 0.01)

        return Point(start_lon, start_lat), Point(end_lon, end_lat)

    async def _do_job(self, route):
        async for point in route.produce_points():
            print(f'User_id = {route.user_id}, point= {point}')
            if point:
                self.producer.produce(
                    topic='coordinates',
                    key=str(route.user_id),
                    value=point.wkt,
                )

    async def produce(self):
        coros = []
        for route in self.routes:
            coros.append(self._do_job(route))
        self.producer.poll(0)
        await asyncio.gather(*coros)


class OriginDistanceHeap:
    def __init__(self, random_points, *, first_point):
        self.heap = [
            (first_point.distance(p), p) for p in random_points
        ]
        heapq.heapify(self.heap)

    def pop(self):
        return heapq.heappop(self.heap)

    @property
    def is_empty(self):
        return not bool(self.heap)


class RandomRoute:
    def __init__(self, first_point, last_point, *, user_id, num_points=None):
        self.first_point = first_point
        self.last_point = last_point
        self.user_id = user_id

        num_points = num_points or random.randint(10, 1000)
        random_points = self._produce_random_points(num_points)
        self.heap = OriginDistanceHeap(random_points, first_point=first_point)

    def _produce_random_points(self, num_points):
        line = LineString([self.first_point, self.last_point])

        intermediate_points = []
        for _ in range(num_points):
            point = line.interpolate(random.random(), True)
            intermediate_points.append(point)

        return intermediate_points

    async def produce_points(self):
        while not self.heap.is_empty:
            _, point = self.heap.pop()
            yield point
            await asyncio.sleep(random.uniform(0.5, 3))
