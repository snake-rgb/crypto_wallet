from config_celery.celery_config import celery


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    pass
