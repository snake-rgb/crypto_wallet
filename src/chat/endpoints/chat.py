from typing import Optional

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from src.chat.models import Message
from src.chat.schemas import MessageSchema
from src.chat.service.chat import ChatService
from src.core.register import RegisterContainer

chat_router = APIRouter(tags=['chat'])


@chat_router.post('/create-message/')
@inject
async def create_message(
        message_schema: MessageSchema,
        chat_service: ChatService = Depends(Provide[RegisterContainer.chat_container.chat_service])
):
    print(message_schema)
    response: Message = await chat_service.create_message(message_schema)
    return {'response': response}


@chat_router.get('/get-messages/')
@inject
async def get_messages(
        limit: Optional[int] = 10,
        chat_service: ChatService = Depends(Provide[RegisterContainer.chat_container.chat_service])
):
    data: list[Message] = await chat_service.get_messages(limit)
    return {'data': data}
