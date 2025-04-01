from sqlalchemy import Column, Integer, String, DateTime, func

from api.db import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    datetime_to_do = Column(DateTime(timezone=True), nullable=False)
    task_info = Column(String(255), nullable=False)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(String(20), nullable=False)
    notification_id = Column(String(36), nullable=False, unique=True)
    message_text = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(String(20), default="PENDING", nullable=False)
