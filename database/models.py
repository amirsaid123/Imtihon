from datetime import datetime
from sqlalchemy import Column, BIGINT, String, DateTime
from sqlalchemy.orm import declarative_base, Mapped
time_zone = "TIMEZONE('Asia/Tashkent', NOW())"

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = Column(BIGINT, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = Column(BIGINT, unique=True)
    user_name: Mapped[str] = Column(String, unique=True, nullable=True)
    first_name: Mapped[str] = Column(String, nullable=True)
    last_name: Mapped[str] = Column(String, nullable=True)
    joined_date: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)


class Chat(Base):
    __tablename__ = 'chats'
    id: Mapped[int] = Column(BIGINT, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = Column(BIGINT, unique=True)
    status: Mapped[int] = Column(String, nullable=True, server_default='True')
