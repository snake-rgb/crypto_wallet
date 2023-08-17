from fastapi_mail import MessageSchema, MessageType, FastMail
from config import settings
from config_celery.celery_config import celery
from asgiref.sync import async_to_sync, sync_to_async
from src.core.register import RegisterContainer
from src.users.services.user import UserService


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    pass


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




@celery.task(retry=True)
def user_chat_activate(
        user_id: int,
        user_service: UserService = RegisterContainer.user_container.user_service()
):
    async_to_sync(user_service.chat_activate)(user_id)
    # user_service.chat_activate(user_id)
    return {'status': user_id}
