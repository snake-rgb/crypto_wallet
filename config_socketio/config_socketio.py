import asyncio
import socketio
from propan import RabbitRouter, RabbitBroker
from propan.brokers.rabbit import RabbitExchange, ExchangeType
from sanic import Sanic
from socketio import AsyncAioPikaManager, AsyncServer
from config import settings
from config.settings import SOCKET_IO_ORIGINS
from src.api.web3_api import Web3API
from src.core.register import RegisterContainer
from sanic.log import logger

sanic_app = Sanic('sanic_app')

manager: AsyncAioPikaManager = socketio.AsyncAioPikaManager(settings.RABBITMQ_URL, write_only=True)
sio: AsyncServer = socketio.AsyncServer(async_mode="sanic", cors_allowed_origins=SOCKET_IO_ORIGINS,
                                        client_manager=manager, logger=True)
sio.attach(sanic_app)

socket_rabbit_router = RabbitRouter()
redis = RegisterContainer.parser_container.redis()


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
        logger.info(latest_block_number)
        async with RabbitBroker(settings.RABBITMQ_URL) as broker:
            await broker.publish(f'{latest_block_number}', queue='last_block_event')

        await asyncio.sleep(5)


@sio.on("connect")
async def connect(
        sid: str,
        environ,
):
    print(f"Client {sid} connected")


@sio.on("disconnect")
async def disconnect(sid):
    print(f"Client {sid} disconnected")


sanic_app.add_task(get_block_latest())
