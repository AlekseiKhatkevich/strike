from confluent_kafka import Consumer
import time
import asyncio
from loguru import logger


conf = {
    'bootstrap.servers': '127.0.0.1:29092',
    'group.id': 'coordinates_consumers',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True,
    # 'max.poll.records': 5,
    'heartbeat.interval.ms': 25000,
    'max.poll.interval.ms': 190000,
    'session.timeout.ms': 180000,
}


class KafkaCoordinatesConsumer:
    """
    """
    def __init__(self, cons_qty, poll_delay=1.0):
        self.cons_qty = cons_qty
        self.poll_delay = poll_delay

    async def _one_consumer(self, number):
        logger.info(f'Starting consumer # {number}')
        # await asyncio.sleep(3.0)
        consumer = Consumer(conf)
        consumer.subscribe(['coordinates'])
        while True:
            msg = consumer.poll()
            if msg is None:
                await asyncio.sleep(self.poll_delay)
            elif err := msg.error():
                print(f"Consumer error happened: {err}")
                continue
            else:
                logger.info(
                    f'Consumer # {number},'
                    f' partition # {msg.partition()},'
                    f' key # {msg.key()},'
                    f' offset # {msg.offset()},'
                    f' value - {msg.value()}'
                )
                # await asyncio.sleep(1.0)

    async def consume(self):
        await asyncio.gather(
            *(self._one_consumer(num) for num in range(self.cons_qty))
        )


