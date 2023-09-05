from typing import Callable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.chat.models import Message
from src.chat.schemas import MessageSchema
from sqlalchemy import desc


class ChatRepository:
    def __init__(self, session_factory: Callable[..., AsyncSession]):
        self.session_factory = session_factory

    async def create_message(self, message_schema: MessageSchema) -> Message:
        async with self.session_factory() as session:
            message = Message(
                text=message_schema.text,
                image=message_schema.image
            )
            session.add(message)
            await session.commit()
            await session.refresh(message)
            return message

    async def get_messages(self, limit: int) -> list[Message]:
        async with self.session_factory() as session:
            query = await session.execute(select(Message).order_by(desc(Message.id)))
            messages = query.scalars().fetchmany(limit)
        return messages
