import socketio
from socketio import AsyncAioPikaManager

from config import settings

fastapi_manager: AsyncAioPikaManager = socketio.AsyncAioPikaManager(settings.RABBITMQ_URL, write_only=True)
