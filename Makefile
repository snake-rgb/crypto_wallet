celery_run:
	celery -A config_celery.celery_config:celery worker --loglevel=INFO

beat_run:
	celery

socketio_run:
	 uvicorn config_socketio.config_socketio:socket_app --port 8001
run:
	uvicorn config_fastapi.app:app --reload --port 8000