celery_run:
	celery -A config_celery.celery_config:celery worker --loglevel=INFO --concurrency 8
make flower_run:
	celery --broker=amqp://guest:guest@rabbitmq:5672// flower
beat_run:
	celery

socketio_run:
	 sanic config_socketio.config_socketio:sanic_app --dev --port 8001 --workers 1 --reload
socketio_client_run:
	python config_socketio/config_socketio_client.py
run:
	uvicorn config_fastapi.app:app --reload --host 0.0.0.0 --port 8000

delivery_run:
	python src/delivery/google_request.py

makemigrations:
	alembic revision --autogenerate
migrate:
	alembic upgrade head

asyncapi_docs:
	python asyncapi/generator.py
	sudo ag asyncapi_docs.yaml @asyncapi/html-template -o static/async_api --force-write
	sudo mv static/async_api/index.html templates/asyncapi_docs
	sudo chmod 746 templates/asyncapi_docs/index.html
	python asyncapi/html_fixer.py

init_database:
	python init_script.py
	make run