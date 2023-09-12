from contextlib import asynccontextmanager
import httpx
import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
import pytest_asyncio
from propan import RabbitBroker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from starlette.middleware.cors import CORSMiddleware
from config import settings
from config.settings import DATABASE_TEST_URL
from config_socketio.config_socketio import sanic_app, redis
from src.core.database import Base
from config_fastapi import routers
from src.core.register import RegisterContainer

broker = RabbitBroker(settings.RABBITMQ_URL, timeout=120)


@pytest.fixture(autouse=True)
async def test_db_engine():
    engine = create_async_engine(DATABASE_TEST_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def app():
    @asynccontextmanager
    async def lifespan(app):
        print("Starting up")
        container = RegisterContainer()
        # app.mount("/socket.io", sanic_app)
        container.core_container.db(db_url=DATABASE_TEST_URL)
        app.container = container
        app.broker = broker
        await broker.start()
        yield
        sanic_app.shutdown_tasks()
        sanic_app.stop()
        await redis.close()
        await broker.close()
        print("Shutting down")

    app = FastAPI(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    routers.init_routers(app)
    async with LifespanManager(app) as manager:
        print("We're in!")
        yield manager.app


@pytest_asyncio.fixture
async def client(app):
    async with LifespanManager(app) as manager:
        async with httpx.AsyncClient(app=manager.app, base_url="http://testserver") as client:
            try:
                print("Client is ready")
                yield client
            finally:
                await client.aclose()
