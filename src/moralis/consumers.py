from propan.brokers.rabbit import RabbitExchange
from config_socketio.config_socketio import socket_rabbit_router
from src.moralis.moralis_api import MoralisAPI
from src.core.register import RegisterContainer

moralis_exchange = RabbitExchange(name='moralis_exchange')


@socket_rabbit_router.handle('get_native_transactions', exchange=moralis_exchange)
async def get_native_transactions(
        data: dict,
):
    moralis_api: MoralisAPI = RegisterContainer.moralis_container.moralis_api()
    limit: int = int(data.get('limit'))
    address: str = data.get('address')
    cursor: str = data.get('cursor')
    page: str = data.get('page')
    transactions: dict = await moralis_api.get_native_transactions(address=address, limit=limit, cursor=cursor,
                                                                   page=page)
    return transactions
