from confluent_kafka import Consumer
import time

print('Starting Kafka Consumer')

conf = {
    'bootstrap.servers': '127.0.0.1:29092',
    'group.id': 'test',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True,
    # 'max.poll.records': 5,
    'heartbeat.interval.ms': 25000,
    'max.poll.interval.ms': 190000,
    'session.timeout.ms': 180000,
}

print("connecting to Kafka topic")

consumer = Consumer(conf)
consumer.subscribe(['test'])

while True:
    msg = consumer.poll(1.0)

    if msg is None:
        continue
    elif err := msg.error():
        print(f"Consumer error happened: {err}")
        continue
    else:
        print("Connected to Topic: {} and Partition : {}".format(msg.topic(), msg.partition()))
        print("Received Message : {} with Offset : {}".format(msg.value().decode('utf-8'), msg.offset()))
        time.sleep(2.5)
