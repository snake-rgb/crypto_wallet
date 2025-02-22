from src.chat.models import Message
from src.chat.repository.chat import ChatRepository
from src.chat.schemas import MessageSchema


class ChatService:
    def __init__(self, chat_repository: ChatRepository):
        self.chat_repository = chat_repository

    async def create_message(self, message_schema: MessageSchema, user_id: int) -> Message:
        return await self.chat_repository.create_message(message_schema, user_id)

    async def get_messages(self, limit: int) -> list[Message]:
        return await self.chat_repository.get_messages(limit)

    async def get_user_messages_count(self, user_id: int) -> int:
        return await self.chat_repository.get_user_messages_count(user_id)
