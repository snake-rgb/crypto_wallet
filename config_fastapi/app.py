from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config_fastapi import broker
from .routers import init_routers
from celery import Celery
from fastapi.staticfiles import StaticFiles
from config_socketio.config_socketio import socket_rabbit_router, sanic_app
from src.core.database import Database
from src.core.register import RegisterContainer

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


@app.on_event('startup')
async def startup():
    container = RegisterContainer()
    db: Database = container.core_container.db()
    celery: Celery = container.celery()
    app.container = container

    app.broker = broker
    app.broker.include_router(socket_rabbit_router)
    await broker.start()
    app.mount("/socket.io", sanic_app, name='socket.io')
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event('shutdown')
async def shutdown():
    await broker.close()
    print('fastapi shutdown')

# @app.get('/last-block/')
# async def set_last_block(
# ):
#     web3_api: Web3API = RegisterContainer.api_container.web3_api()
#     redis = RegisterContainer.parser_container.redis()
#     await redis.set('last_block_number', await web3_api.get_block_number_latest())
