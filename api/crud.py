import json
import jwt
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timedelta


from api.db import producer
from api.models import Task, Message
from api.schemas import TaskPost, TaskPatch, MessageGet, TokenRequest
from config import KAFKA_TOPIC, JWT_SECRET_KEY, JWT_ALGORITHM


async def get_all_tasks(db: AsyncSession):
    result = await db.execute(select(Task))
    return result.scalars().all()


async def get_task(db: AsyncSession, task_id: int):
    result = await db.execute(select(Task).filter(Task.id == task_id))
    return result.scalar_one_or_none()


async def create_task(db: AsyncSession, task: TaskPost):
    db_task = Task(**task.dict())
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def update_task(db: AsyncSession, task_id: int, task: TaskPatch):
    await db.execute(
        update(Task).where(Task.id == task_id).values(**task.dict(exclude_unset=True))
    )
    await db.commit()
    return await get_task(db, task_id)


async def create_message(db: AsyncSession, message: MessageGet):
    existing = await db.execute(select(Message).where(Message.notification_id == message.notification_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Message with this notification_id already exist")

    new_message = Message(
        telegram_user_id=message.telegram_user_id,
        notification_id=message.notification_id,
        message_text=message.message_text
    )
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)

    try:
        producer.begin_transaction()
        payload = {
            "id": new_message.id,
            "telegram_user_id": new_message.telegram_user_id,
            "notification_id": new_message.notification_id,
            "message_text": new_message.message_text,
            "status": new_message.status
        }
        producer.produce(KAFKA_TOPIC, value=json.dumps(payload).encode("utf-8"))
        producer.flush()
        producer.commit_transaction()
    except Exception as e:
        producer.abort_transaction()
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to send to Kafka: {str(e)}")

    return new_message


async def get_all_messages(db: AsyncSession):
    result = await db.execute(select(Message))
    return result.scalars().all()


async def get_token(request: TokenRequest):
    if request.username != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username",
        )

    payload = {
        "sub": request.username,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    return {"access_token": token, "token_type": "bearer"}
