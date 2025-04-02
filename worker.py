import json
import asyncio
from confluent_kafka import KafkaException, Consumer
from sqlalchemy import update

from api.models import Message
from api.db import async_session, bot
from config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC

def create_kafka_comsumer():
    consumer = Consumer({
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": "notification_worker_group",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False
    })
    consumer.subscribe([KAFKA_TOPIC])
    return consumer


async def process_message(msg):
    try:
        payload = json.loads(msg.value().decode("utf-8"))
        message_id = payload["id"]
        telegram_user_id = payload["telegram_user_id"]
        message_text = payload["message_text"]

        await bot.send_message(chat_id=telegram_user_id, text=message_text)

        async with async_session() as session:
            await session.execute(
                update(Message)
                .where(Message.id == message_id)
                .values(status="SENT")
            )
            await session.commit()

    except Exception as e:
        async with async_session() as session:
            await session.execute(
                update(Message)
                .where(Message.id == message_id)
                .values(status="FAILED")
            )
            await session.commit()
        print(f"Failed to process message: {str(e)}")

    consumer.commit(msg)


async def consume():
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            raise KafkaException(msg.error())
        await process_message(msg)

if __name__ == "__main__":
    consumer = create_kafka_comsumer()
    asyncio.run(consume())
