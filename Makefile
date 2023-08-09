celery_run:
	celery -A config_celery.celery_config:celery worker --loglevel=INFO

beat_run:
	celery

run:
	uvicorn config_fastapi.app:app --reload --port 8001