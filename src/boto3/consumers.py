from propan.brokers.rabbit import RabbitExchange

from config_socketio.config_socketio import socket_rabbit_router
from src.boto3.services.boto3 import Boto3Service
from src.core.register import RegisterContainer

boto3_exchange = RabbitExchange(name='boto3_exchange')


@socket_rabbit_router.handle('upload_image', exchange=boto3_exchange)
async def upload_image(
        data
):
    boto3_service: Boto3Service = RegisterContainer.boto3_container.boto3_service()
    return await boto3_service.upload_image(
        base64_image=data.get('image'),
    )
