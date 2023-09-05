from typing import Optional

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from src.boto3.services.boto3 import Boto3Service
from src.chat.models import Message
from src.chat.schemas import MessageSchema
from src.chat.service.chat import ChatService
from src.core.register import RegisterContainer

chat_router = APIRouter(tags=['chat'])


@chat_router.post('/create-message/')
@inject
async def create_message(
        message_schema: MessageSchema,
        chat_service: ChatService = Depends(Provide[RegisterContainer.chat_container.chat_service]),
        boto3_service: Boto3Service = Depends(Provide[RegisterContainer.boto3_container.boto3_service])
):
    if message_schema.image != '':
        image = await boto3_service.upload_image(message_schema.image)
        message_schema.image = image
    response: Message = await chat_service.create_message(message_schema)
    return {'response': response}


@chat_router.get('/get-messages/')
@inject
async def get_messages(
        limit: Optional[int] = 10,
        chat_service: ChatService = Depends(Provide[RegisterContainer.chat_container.chat_service])
):
    messages: list[Message] = await chat_service.get_messages(limit)
    return {'messages': messages}
