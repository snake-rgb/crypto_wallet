from propan.brokers.rabbit import RabbitExchange
from config_socketio.config_socketio import socket_rabbit_router
from src.moralis.moralis_api import MoralisAPI
from src.core.register import RegisterContainer
from src.users.models import User
from src.users.services.user import UserService

user_exchange = RabbitExchange(name='user_exchange')


@socket_rabbit_router.handle('get_user_id', exchange=user_exchange)
async def get_user_id(
        data: dict,
):
    user_service: UserService = RegisterContainer.user_container.user_service()
    user: User = await user_service.profile(data.get('access_token'))
    return user.id
