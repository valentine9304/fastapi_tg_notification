from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from aiogram import Bot

from config import DATABASE_URL, TELEGRAM_TOKEN

bot = Bot(token=TELEGRAM_TOKEN)
Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
