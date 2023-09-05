import asyncio
import datetime

from celery import Celery
from fastapi import FastAPI, Request
from hexbytes import HexBytes
from propan import RabbitBroker
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from src.web3.web3_api import Web3API
from src.ibay.services.ibay import IbayService
from src.wallet.service.wallet import WalletService
from .routers import init_routers
from config_socketio.config_socketio import socket_rabbit_router, sio, sanic_app
from src.core.database import Database
from src.core.register import RegisterContainer
from src.delivery.google_request import run_delivery

templates = Jinja2Templates(directory='templates')
broker = RabbitBroker(settings.RABBITMQ_URL, timeout=120)
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
        allow_origins=['*'],
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
    ibay_service: IbayService = RegisterContainer.ibay_container.ibay_service()
    hash = b'\t\xe2\xb1"\xcf\xa9\'\xe6\xfe\xd8bk\x136:\x12\x91\x15\xfe\x7fm+gK\xf6z\xdd*v\xc9\xf6\xaa'.hex()
    print(hash)


@app.get('/last-block/')
async def set_last_block(
):
    web3_api: Web3API = RegisterContainer.api_container.web3_api()
    redis = RegisterContainer.parser_container.redis()
    await redis.set('last_block_number', await web3_api.get_block_number_latest())
