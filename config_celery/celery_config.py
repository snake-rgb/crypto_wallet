from celery import Celery
import os
from config import settings

celery = Celery('celery',
                broker=settings.RABBITMQ_URL,
                include=['src.celery.user_tasks'],
                backend=settings.CELERY_RESULT_BACKEND,
                )
