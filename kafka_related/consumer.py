import asyncio
from collections import defaultdict

from confluent_kafka import Consumer
from loguru import logger

conf = {
    'bootstrap.servers': '127.0.0.1:29092',
    'group.id': 'coordinates_consumers1',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True,
    'heartbeat.interval.ms': 3000,
}


class KafkaCoordinatesConsumer:
    """
    """

    def __init__(self, cons_qty, poll_delay=1):
        self.cons_qty = cons_qty
        self.poll_delay = poll_delay
        self.cons_user_id_map = defaultdict(set)
        self.consumers = [Consumer(conf) for _ in range(self.cons_qty)]
        for cons in self.consumers:
            cons.subscribe(['coordinates'])

    async def _one_consumer(self, number, consumer):
        logger.info(f'Starting consumer # {number}')

        while True:
            await asyncio.sleep(0.0)
            msg = consumer.poll(0.1)
            if msg is None:
                logger.warning(f'Consumer # {number}, Could not get message')
                await asyncio.sleep(self.poll_delay)
                continue
            elif err := msg.error():
                logger.error(f"Consumer error happened: {err}")
                continue
            else:
                logger.info(
                    f'Consumer # {number},'
                    f' partition # {msg.partition()},'
                    f' key # {msg.key()},'
                    f' offset # {msg.offset()},'
                    f' value - {msg.value()}'
                )
                self.cons_user_id_map[number].add(msg.key())

    async def consume(self):
        coros = []
        for num, cons in enumerate(self.consumers):
            coro = self._one_consumer(num, cons)
            coros.append(coro)

        try:
            await asyncio.gather(*coros)
        finally:
            for cons in self.consumers:
                cons.close()
                logger.info(f'Closing consumer {cons}')

