from fastapi import HTTPException

from config_fastapi.socketio_manager import fastapi_manager
from src.boto3.services.boto3 import Boto3Service
from src.chat.repository.chat import ChatRepository
from src.chat.schemas import MessageSchema


class ChatService:
    def __init__(self, chat_repository: ChatRepository, boto3_service: Boto3Service):
        self.chat_repository = chat_repository
        self.boto3_service = boto3_service

    async def create_message(self, message_schema: MessageSchema):
        if message_schema.image != '':
            image = await self.boto3_service.upload_image(message_schema.image)
            message_schema.image = image
        return await self.chat_repository.create_message(message_schema)

        # raise HTTPException(status_code=400, detail='Cant upload image')

    async def get_messages(self, limit: int):
        return await self.chat_repository.get_messages(limit)
