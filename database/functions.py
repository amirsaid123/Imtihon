from datetime import datetime

from sqlalchemy import delete

from database.models import User, Chat
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
async def insert_user(
    session: AsyncSession,
    telegram_id: int,
    username: str,
    first_name: str,
    last_name: str,
    joined_date: datetime,
):
    stmt = select(User).filter(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if not existing_user:
        new_user = User(
            telegram_id=telegram_id,
            user_name=username,
            first_name=first_name,
            last_name=last_name,
            joined_date = joined_date
        )
        session.add(new_user)
        await session.commit()
        return new_user

    return existing_user

async def insert_chat(session: AsyncSession, telegram_id: int):
    stmt = select(Chat).filter(Chat.telegram_id == telegram_id)
    result = await session.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if not existing_user:
        new_user = Chat(
            telegram_id=telegram_id,
        )
        session.add(new_user)
        await session.commit()
        return new_user

    return existing_user

async def get_all_chats(session: AsyncSession):
    stmt = select(Chat)
    result = await session.execute(stmt)
    users = result.scalars().all()
    return users

async def change_status(session: AsyncSession, chat_id: int) -> None:
    stmt = select(Chat).filter(Chat.telegram_id == chat_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise ValueError(f"User with ID {chat_id} does not exist.")

    user.status = False
    await session.commit()

async def delete_chats(session: AsyncSession, chat_id: int) -> None:

    stmt = delete(Chat).where(Chat.telegram_id == chat_id)
    result = await session.execute(stmt)
    await session.commit()

async def get_user_id_by_telegram_id(session: AsyncSession, telegram_id: int) -> int | None:
    stmt = select(User.id).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)
    user_id = result.scalar_one_or_none()
    return user_id


