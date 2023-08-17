import asyncio
import socketio
from propan import RabbitBroker
from propan.brokers.rabbit import RabbitExchange, ExchangeType, RabbitQueue
from propan import RabbitRouter
from config import settings
from config.settings import SOCKET_IO_ORIGINS
from src.api.web3_api import Web3API
from src.core.register import RegisterContainer

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=SOCKET_IO_ORIGINS)
socket_app = socketio.ASGIApp(sio)

socket_rabbit_router = RabbitRouter()


# TODO: Получать номер последнего блока, прокидывать цепочку блоков в сервис

async def get_block_latest(
        sid: str,
        web3_api: Web3API = RegisterContainer.api_container.web3_api()
):
    while True:
        latest_block_number = str(await web3_api.get_block_number_latest())
        async with RabbitBroker(settings.RABBITMQ_URL) as broker:
            await broker.publish(f'{latest_block_number}', queue='last_block_event')
        await asyncio.sleep(10)


@sio.on("connect")
async def connect(
        sid: str,
        environ,
):
    print(f"Client {sid} connected")
    # send event
    asyncio.create_task(get_block_latest(sid))


@sio.on("disconnect")
async def disconnect(sid):
    print(f"Client {sid} disconnected")


queue1 = RabbitQueue(name='queue1')
rabbit_exchange = RabbitExchange(name='rabbit_exchange', type=ExchangeType.FANOUT)


@socket_rabbit_router.handle(queue=queue1, exchange=rabbit_exchange)
async def test():
    print('rabbit test')
