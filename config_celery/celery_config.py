from celery import Celery
from config import settings
from src.core.register import RegisterContainer

celery = Celery(__name__,
                broker=settings.RABBITMQ_URL,
                include=['src.users.tasks'],
                backend=settings.CELERY_RESULT_BACKEND,
                broker_connection_retry_on_startup=True)
celery.container = RegisterContainer()
