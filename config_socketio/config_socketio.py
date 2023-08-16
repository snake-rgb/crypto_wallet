import asyncio
import socketio
from aio_pika import Message
from dependency_injector.wiring import Provide, inject
from propan import RabbitBroker
from propan.annotations import Logger
from propan.brokers.rabbit import RabbitExchange, ExchangeType, RabbitQueue
from propan import RabbitRouter
from web3 import Web3, WebsocketProvider
from config.settings import SOCKET_IO_ORIGINS
from src.core.register import RegisterContainer

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=SOCKET_IO_ORIGINS)
socket_app = socketio.ASGIApp(sio)

web3_api = Web3(WebsocketProvider(
    'wss://wild-small-wish.ethereum-sepolia.discover.quiknode.pro/473dd971207e048428b1377f87c8a94c8bf95cc8/'))
socket_rabbit_router = RabbitRouter()


@inject
async def get_block_latest(
        sid,
        web3: Web3,
):
    while True:
        latest_block = web3.eth.get_block('latest')
        print(latest_block)

        await asyncio.sleep(10)


@sio.on("connect")
async def connect(
        sid,
        environ,
):
    print(f"Client {sid} connected")
    # send event
    async with RabbitBroker("amqp://guest:guest@localhost:5672/") as broker:
        await broker.publish('rabbit message', queue='event1')

    asyncio.create_task(get_block_latest(sid, web3_api))


@sio.on("disconnect")
async def disconnect(sid):
    print(f"Client {sid} disconnected")


queue1 = RabbitQueue(name='queue1')
rabbit_exchange = RabbitExchange(name='rabbit_exchange', type=ExchangeType.FANOUT)


@socket_rabbit_router.handle(queue=queue1, exchange=rabbit_exchange)
async def test():
    print('rabbit test')
