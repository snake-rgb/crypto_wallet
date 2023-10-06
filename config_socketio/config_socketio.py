import json

import socketio
from dependency_injector.wiring import Provide, inject
import asyncio
from propan import RabbitBroker
from aioredis import Redis
from sanic import Sanic
from socketio import AsyncAioPikaManager, AsyncServer
from config import settings
from src.users.services.user import UserService
from src.core.register import RegisterContainer
from src.ibay.services.ibay import IbayService
from src.web3.web3_api import Web3API
from sanic.log import logger

redis: Redis = RegisterContainer.parser_container.redis()
manager: AsyncAioPikaManager = socketio.AsyncAioPikaManager(settings.RABBITMQ_URL)
sio: AsyncServer = socketio.AsyncServer(async_mode="sanic", cors_allowed_origins='*',
                                        client_manager=manager, namespaces=['*'])
sanic_app = Sanic('sanic_app')
sio.attach(sanic_app)


@sio.on("connect")
async def connect(
        sid: str,
        environ,
):
    print(f'Client connected {sid}')


@sio.on("disconnect")
@inject
async def disconnect(sid,
                     user_service: UserService = Provide[RegisterContainer.user_container.user_service]
                     ):
    sio.leave_room(sid, room='chat_room')
    session = await sio.get_session(sid)
    access_token = session.get('access_token')
    user = await user_service.profile(access_token)
    await sio.emit('leave_chat', room='chat_room', data={'user_id': user.id})
    await remove_user_from_redis(sid)
    print(f"Client {sid} disconnected")


@sio.on("event_subscription")
@inject
async def event_subscription(
        sid: str,
        data,
        user_service: UserService = Provide[RegisterContainer.user_container.user_service],
):
    user = await user_service.profile(data.get('access_token'))
    await sio.save_session(sid, {'access_token': data.get('access_token'), 'user_id': user.id})
    sio.enter_room(sid, room=user.id)
    print(f"Client {sid} connected to event room")


@sio.on("join_chat")
@inject
async def join_chat(sid,
                    data,
                    user_service: UserService = Provide[RegisterContainer.user_container.user_service]
                    ):
    sio.enter_room(sid, room='chat_room')
    print(f"Client {sid} connected chat")
    print(f"Join chat {data}")
    access_token: str = str(data.get('access_token'))
    print(access_token)
    user = await user_service.profile(access_token)
    print(user)
    await sio.save_session(sid, {'access_token': access_token, 'user_id': user.id})

    await add_user_to_redis(sid, {sid: {
        'user_id': user.id,
        'username': user.username,
        'profile_image': user.profile_image,
        'sid': sid,
    }})
    await sio.emit('join_chat', list(json.loads(await redis.get('online_users')).values()))


@sio.on('send_message')
async def send_message(sid, data):
    session = await sio.get_session(sid)
    user_id = session.get('user_id')
    await sio.emit('send_message',
                   data,
                   )


async def add_user_to_redis(sid, data: dict):
    if await redis.get('online_users') is not None:
        online_users = json.loads(await redis.get('online_users'))
        online_users[sid] = data.get(sid)
        print('Online users add user to redis', online_users)
        await redis.set('online_users', json.dumps(online_users))
    else:
        await redis.set('online_users', json.dumps(data))


async def remove_user_from_redis(sid):
    try:
        online_users: dict = json.loads(await redis.get('online_users'))
        online_users.pop(sid)
        await redis.set('online_users', json.dumps(online_users))
    except KeyError:
        pass


@sanic_app.after_reload_trigger
@sanic_app.main_process_start
async def main_start(sanic):
    logger.info('sanic startup')
    last_block_number = await redis.get('last_block_number')
    logger.info(last_block_number)


@sanic_app.after_server_stop
def server_stop(app, loop):
    sanic_app.purge_tasks()
    asyncio.get_event_loop().stop()


@sanic_app.before_server_start
async def setup_container(app, _):
    await redis.delete('online_users')
    app.ext.dependency(RegisterContainer())


async def get_block_latest(
        web3_api: Web3API = RegisterContainer.web3_container.web3_api(),
):
    while True:
        latest_block_number: str = str(await web3_api.get_block_number_latest())
        redis_last_block_bytes: bytes = await redis.get('last_block_number')
        if redis_last_block_bytes:
            redis_last_block_number: str = redis_last_block_bytes.decode('utf-8')
        else:
            redis_last_block_number: str = latest_block_number
        logger.info(f'{redis_last_block_number} - {latest_block_number}')
        # send last block number
        async with RabbitBroker(settings.RABBITMQ_URL) as broker:
            await broker.publish(f'{latest_block_number}', queue='start_parse', exchange='parser_exchange')

        await asyncio.sleep(1)


@inject
async def delivery(ibay_service: IbayService = Provide[RegisterContainer.ibay_container.ibay_service]):
    while True:
        await ibay_service.delivery()
        await asyncio.sleep(5)

# sanic_app.add_task(delivery())
# sanic_app.add_task(get_block_latest())
