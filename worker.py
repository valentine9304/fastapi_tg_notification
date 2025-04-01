import json
import asyncio
from confluent_kafka import KafkaException
from sqlalchemy import update

from api.models import Message
from api.db import async_session, bot, consumer


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
    asyncio.run(consume())
