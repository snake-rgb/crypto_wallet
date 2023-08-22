from celery import Celery
from fastapi import FastAPI, Request
from propan import RabbitBroker
import logging

from propan.brokers.rabbit import RabbitExchange, ExchangeType
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from src.api.web3_api import Web3API
from .routers import init_routers
from config_socketio.config_socketio import socket_rabbit_router, manager, sio, sanic_app
from src.core.database import Database
from src.core.register import RegisterContainer

templates = Jinja2Templates(directory='templates')
broker = RabbitBroker(settings.RABBITMQ_URL)

# Настройки CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001",
]


def create_app() -> FastAPI:
    # fast api
    fast_api_app = FastAPI()

    fast_api_app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    init_routers(fast_api_app)

    return fast_api_app


app = create_app()


@app.get("/index/", response_class=HTMLResponse, )
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {'request': request})


@app.on_event('startup')
async def startup():
    container = RegisterContainer()

    db: Database = container.core_container.db()
    celery: Celery = container.celery()
    app.container = container

    app.broker = broker
    app.broker.include_router(socket_rabbit_router)
    await broker.start()
    app.mount("/socket.io", sanic_app)


@app.on_event('shutdown')
async def shutdown():
    await broker.close()
    print('fastapi shutdown')


@app.get('/test/hello/')
async def test(
):
    web3_api: Web3API = RegisterContainer.api_container.web3_api()
    # async with RabbitBroker(settings.RABBITMQ_URL) as broker:
    #     await broker.publish(f'publish from fastapi',
    #                          exchange=RabbitExchange(name='socketio', type=ExchangeType.FANOUT))
    # await sio.emit(event='chat_message', namespace='/chat', room='chat_room', data={'message': 'hello world'})
    # print(await web3_api.web3.eth.get_transaction_receipt(
    #     '0x16ef2f05d628c59522f6b42d2d2afa0b3210f0869ad5e130c4c004ef1d75666f'))
