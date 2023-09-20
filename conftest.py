import asyncio
from asyncio import get_event_loop
from contextlib import asynccontextmanager
import httpx
import passlib.hash
import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
import pytest_asyncio
from propan import RabbitBroker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from starlette.middleware.cors import CORSMiddleware
from config import settings
from config.settings import DATABASE_TEST_URL
from config_socketio.config_socketio import sanic_app, redis
from src.core.database import Base
from config_fastapi import routers
from src.core.register import RegisterContainer
from src.ibay.models import Product
from src.users.models import User
from src.wallet.models import Asset, Wallet

broker = RabbitBroker(settings.RABBITMQ_URL, timeout=120)


@pytest.fixture(autouse=True)
async def test_db_engine():
    engine = create_async_engine(DATABASE_TEST_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        session = AsyncSession(bind=conn)
        # create instances for test
        await create_user(session)
        await create_product(session)
        await create_asset(session)
        await create_wallet(session)
    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def app():
    @asynccontextmanager
    async def lifespan(app):
        container = RegisterContainer()
        app.mount("/socket.io", sanic_app)
        container.core_container.db(db_url=DATABASE_TEST_URL)
        app.container = container
        app.broker = broker
        await broker.start()
        yield
        sanic_app.shutdown_tasks()
        sanic_app.stop()
        await redis.close()
        await broker.close()

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
        yield manager.app


@pytest.fixture(scope="session")
def event_loop():
    loop = get_event_loop()
    yield loop


@pytest_asyncio.fixture
async def client(event_loop, app):
    async with LifespanManager(app) as manager:
        async with httpx.AsyncClient(app=manager.app, base_url="http://testserver") as client:
            yield client
            await client.aclose()


@pytest_asyncio.fixture
async def auth_user(client):
    response = await client.post('/api/v1/login/', json={
        'email': 'user@user.com',
        'password': '1230123viK',
        'remember_me': 'true'
    })


async def create_user(session: AsyncSession):
    user = User(
        username='username_test',
        email='user@user.com',
        password=passlib.hash.pbkdf2_sha256.hash('1230123viK')
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)


async def create_product(session: AsyncSession):
    product = Product(

        name='product_name_test',
        image="https://cryptowalletbucket.s3.eu-north-1.amazonaws.com/images/326e3754-7feb-4973-8073-a487b77f8fe0.jpg",
        price=0.000001,
        wallet_address="0xD8f38DaA59799900b9629622b8D9B17a3CfD4bA9"

    )
    session.add(product)
    await session.commit()
    await session.refresh(product)


async def create_asset(session: AsyncSession):
    asset = Asset(
        short_name='SETH',
        decimal_places=18,
        symbol='SepoliaETH',
        image='https://cryptowalletbucket.s3.eu-north-1.amazonaws.com/images/ethereum.png'
    )
    session.add(asset)
    await session.commit()
    await session.refresh(asset)


async def create_wallet(session: AsyncSession):
    wallet = Wallet(
        address='0x9841b300b8853e47b7265dfF47FD831642e649e0',
        balance=1,
        private_key='14aa0a8e2f21b8881cde0a34d3d5a356feb548d4b9d4c4233775c2f651f1058a',
        user_id=1,
        asset_id=1,
    )
    session.add(wallet)
    await session.commit()
    await session.refresh(wallet)
