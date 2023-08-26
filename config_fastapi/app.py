from celery import Celery
from fastapi import FastAPI, Request
from propan import RabbitBroker
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from src.api.web3_api import Web3API
from src.wallet.service.wallet import WalletService
from .routers import init_routers
from config_socketio.config_socketio import socket_rabbit_router, sio, sanic_app
from src.core.database import Database
from src.core.register import RegisterContainer

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
    web3_api: Web3API = RegisterContainer.api_container.web3_api()
    wallet_service: WalletService = RegisterContainer.wallet_container.wallet_service()
