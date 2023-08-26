import asyncio

import engineio
import socketio
from propan import RabbitRouter, RabbitBroker
from propan.brokers.rabbit import RabbitExchange, ExchangeType
from sanic import Sanic
from socketio import AsyncAioPikaManager, AsyncServer
from config import settings
from config_fastapi.socketio_manager import fastapi_manager
from src.api.web3_api import Web3API
from src.core.register import RegisterContainer
from sanic.log import logger

sanic_app = Sanic('sanic_app')

manager: AsyncAioPikaManager = socketio.AsyncAioPikaManager(settings.RABBITMQ_URL)
sio: AsyncServer = socketio.AsyncServer(async_mode="sanic", cors_allowed_origins='*',
                                        client_manager=manager, namespaces=['*'])
sio.attach(sanic_app)
socket_rabbit_router = RabbitRouter()
redis = RegisterContainer.parser_container.redis()


@sanic_app.after_reload_trigger
@sanic_app.main_process_start
async def main_start(sanic: Sanic):
    logger.info('sanic startup')
    last_block_number = await redis.get('last_block_number')
    logger.info(last_block_number)


async def get_block_latest(
        web3_api: Web3API = RegisterContainer.api_container.web3_api(),
):
    while True:
        latest_block_number: str = str(await web3_api.get_block_number_latest())
        redis_last_block_bytes: bytes = await redis.get('last_block_number')
        redis_last_block_number: str = redis_last_block_bytes.decode('utf-8')
        logger.info(f'{redis_last_block_number} - {latest_block_number}')
        # send last block number
        async with RabbitBroker(settings.RABBITMQ_URL) as broker:
            await broker.publish(f'{latest_block_number}', queue='last_block_event')

        await asyncio.sleep(1)


@sio.on("connect", namespace='/chat')
async def connect(
        sid: str,
        environ,
):
    print(f"Client {sid} connected chat")
    # await fastapi_manager.emit('chat_message', {'data': 'Server generated event'}, room=sid)


@sio.on("disconnect", namespace='/chat')
async def disconnect(sid):
    print(f"Client {sid} disconnected")


sanic_app.add_task(get_block_latest())


@sio.on("chat", namespace='/chat')
async def chat(sid, data):
    message = data.get('message')
    await fastapi_manager.emit('chat_message', data={'message': f'{message}'}, namespace='/chat')
