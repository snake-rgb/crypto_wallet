from dependency_injector.wiring import inject, Provide
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin
from config import settings
from src.auth.dependencies.jwt_auth import decode_token
from src.sqladmin.auth import AdminAuth
from src.users.services.user import UserService
from .config_fastapi import broker, rabbit_router
from .routers import init_routers
from celery import Celery
from fastapi.staticfiles import StaticFiles
from config_socketio.config_socketio import sanic_app
from src.core.database import Database
from src.core.register import RegisterContainer
from .sqladmin_views_routes import init_sqladmin_routes

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
admin = Admin(app, RegisterContainer.core_container.db().engine,
              authentication_backend=AdminAuth(secret_key=settings.SECRET_KEY),
              logo_url='/static/assets/img/favicon/favicon.ico')


@app.on_event('startup')
async def startup():
    container = RegisterContainer()
    db: Database = container.core_container.db()
    celery: Celery = container.celery()
    app.container = container

    app.broker = broker
    await init_sqladmin_routes(admin)
    app.broker.include_router(rabbit_router)
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
#     web3_api: Web3API = RegisterContainer.web3_container.web3_api()
#     redis = RegisterContainer.parser_container.redis()
#     await redis.set('last_block_number', await web3_api.get_block_number_latest())

@app.get('/test/')
@inject
async def test(
        user_service: UserService = Depends(Provide[RegisterContainer.user_container.user_service])
):
    result = decode_token(
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjcsImlhdCI6MTY5NjU5NjYzMSwidHlwZSI6IkJlYXJlciJ9.r140hY5omc-4TMgr7zqCCbB2Qx111ULIP-m8cTtu81Y')
    return result
