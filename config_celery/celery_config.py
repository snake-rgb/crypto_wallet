from celery import Celery
from config import settings

celery = Celery('celery',
                broker=settings.RABBITMQ_URL,
                include=['src.users.tasks'],
                backend=settings.CELERY_RESULT_BACKEND,
                )
