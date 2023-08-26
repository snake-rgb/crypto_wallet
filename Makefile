celery_run:
	celery -A config_celery.celery_config:celery worker --loglevel=INFO
make flower_run:
	celery --broker=amqp://guest:guest@localhost:5672// flower
beat_run:
	celery

socketio_run:
	 sanic config_socketio.config_socketio:sanic_app --dev --port 8001 --workers 1 --reload
socketio_client_run:
	python config_socketio/config_socketio_client.py
run:
	uvicorn config_fastapi.app:app --reload --port 8000

makemigrations:
	alembic revision --autogenerate
migrate:
	alembic upgrade head