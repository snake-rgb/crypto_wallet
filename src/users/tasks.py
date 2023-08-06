from config_celery.celery_config import celery
import time


@celery.task
def sample_task():
    for i in range(5):
        time.sleep(1)
    return {'status': 'hello world'}
