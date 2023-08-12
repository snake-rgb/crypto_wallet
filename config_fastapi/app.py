import os.path

from fastapi import FastAPI, Request
from propan.fastapi import RabbitRouter
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from config import settings
from config_socketio.config_socketio import socket_app
from src.auth.endpoints.auth import auth_router
from src.core.database import Database
from src.core.register import RegisterContainer
from src.users.endpoints.user_endpoints import register_router, user_rabbit_router
from src.wallet.endpoints.wallet import wallet_router

rabbit_router = RabbitRouter(settings.RABBITMQ_URL)

templates = Jinja2Templates(directory='templates')

# Настройки CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001",
]


def create_app() -> FastAPI:
    container = RegisterContainer()
    db: Database = container.core_container.db()
    # db.create_database()
    # fast api
    fast_api_app = FastAPI(lifespan=user_rabbit_router.lifespan_context)

    fast_api_app.container = container

    fast_api_app.include_router(register_router)
    fast_api_app.include_router(auth_router)
    fast_api_app.include_router(user_rabbit_router)
    fast_api_app.include_router(wallet_router)
    fast_api_app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    fast_api_app.mount("/socket.io", socket_app)

    return fast_api_app


app = create_app()


@app.get("/index/", response_class=HTMLResponse,)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {'request': request})
