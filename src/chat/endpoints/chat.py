from typing import Optional

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials

from src.auth.dependencies.jwt_auth import decode_token
from src.auth.endpoints.auth import user_auth
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
        boto3_service: Boto3Service = Depends(Provide[RegisterContainer.boto3_container.boto3_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),
):
    if message_schema.image != '':
        image = await boto3_service.upload_image(message_schema.image)
        message_schema.image = image
        payload = decode_token(bearer.credentials)
        message: Message = await chat_service.create_message(message_schema, user_id=payload.get('user_id'))
        return {'message': message}


@chat_router.get('/get-messages/')
@inject
async def get_messages(
        limit: Optional[int] = 10,
        chat_service: ChatService = Depends(Provide[RegisterContainer.chat_container.chat_service])
):
    messages: list[Message] = await chat_service.get_messages(limit)
    return {'messages': messages}


@chat_router.get('/get-user-messages-count/')
@inject
async def get_user_messages_count(
        user_id: int,
        chat_service: ChatService = Depends(Provide[RegisterContainer.chat_container.chat_service])
):
    messages_count: int = await chat_service.get_user_messages_count(user_id)
    return {'messages_count': messages_count}
