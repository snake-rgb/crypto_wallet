import asyncio
from dependency_injector.wiring import Provide, inject
from fastapi_mail import MessageSchema, MessageType, FastMail
from config import settings
from asgiref.sync import async_to_sync
from src.core.register import RegisterContainer
from src.users.services.user import UserService

celery = RegisterContainer.celery()


@celery.task
def send_register_email(email: str, username: str) -> dict:
    message = MessageSchema(
        subject="Hello!",
        recipients=[email],
        template_body={'username': username},
        subtype=MessageType.html
    )
    fm = FastMail(settings.EMAIL_CONF)
    async_to_sync(fm.send_message)(message, template_name='email_template.html')
    return {'status': 'success'}


@celery.task
@inject
def user_chat_activate(
        user_id: int,
        user_service: UserService = Provide[RegisterContainer.user_container.user_service]
):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(user_service.chat_activate(user_id))
    return {'status': user_id}
