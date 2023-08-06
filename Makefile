celery_run:
	celery -A config_celery.celery_config:celery worker --loglevel=INFO