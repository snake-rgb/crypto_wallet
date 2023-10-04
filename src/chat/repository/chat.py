import datetime
from typing import Callable

import pytz
from sqlalchemy import select, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.functions import count

from src.chat.models import Message
from src.chat.schemas import MessageSchema
from sqlalchemy import desc

from src.users.models import User


class ChatRepository:
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory

    async def create_message(self, message_schema: MessageSchema, user_id: int) -> Message:
        async with self.session_factory() as session:
            message = Message(
                text=message_schema.text,
                image=message_schema.image,
                user_id=user_id,
                date=datetime.datetime.now()
            )
            session.add(message)
            await session.commit()
            await session.refresh(message)
            return message

    async def get_messages(self, limit: int) -> list[Message]:
        async with self.session_factory() as session:
            query = await session.execute(
                select(Message).options(joinedload(Message.user)).order_by(desc(Message.date)))
            messages = query.scalars().fetchmany(limit)
        return messages[::-1]

    async def get_user_messages_count(self, user_id: int) -> int:
        async with self.session_factory() as session:
            query = await session.execute(select(Message).where(Message.user_id == user_id))
            messages = query.scalars().all()
        return len(messages)
