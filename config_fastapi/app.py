from fastapi import FastAPI, Request
from propan import RabbitBroker
from propan.fastapi import RabbitRouter
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from .routers import init_routers
from config_socketio.config_socketio import socket_app
from src.core.database import Database
from src.core.register import RegisterContainer

rabbit_router = RabbitRouter(settings.RABBITMQ_URL, prefix='/app')
templates = Jinja2Templates(directory='templates')
broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
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
    fast_api_app.mount("/socket.io", socket_app)
    return fast_api_app


app = create_app()


@app.get("/index/", response_class=HTMLResponse, )
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {'request': request})


@app.on_event('startup')
async def startup():
    container = RegisterContainer()
    db: Database = container.core_container.db()
    app.container = container
    print('fastapi startup')


@app.on_event('shutdown')
async def shutdown():
    print('fastapi shutdown')
