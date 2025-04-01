import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from confluent_kafka import Producer, Consumer
from confluent_kafka.admin import AdminClient, NewTopic
from aiogram import Bot

from config import DATABASE_URL, KAFKA_BOOTSTRAP_SERVERS, TELEGRAM_TOKEN, KAFKA_TOPIC

bot = Bot(token=TELEGRAM_TOKEN)
Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


producer = Producer({
    "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
    "transactional.id": "todo-producer",
    "enable.idempotence": True,
})
producer.init_transactions()

admin_client = AdminClient({
    "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS
})
new_topic = NewTopic(topic=KAFKA_TOPIC, num_partitions=1, replication_factor=1)
fs = admin_client.create_topics([new_topic])

for topic, f in fs.items():
    try:
        f.result()
        print(f"Топик '{topic}' создан.")
    except Exception as e:
        print(f"Не удалось создать топик '{topic}': {e}")

consumer = Consumer({
    "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
    "group.id": "notification_worker_group",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False
})
consumer.subscribe([KAFKA_TOPIC])
