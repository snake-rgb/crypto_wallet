from propan.brokers.rabbit import RabbitExchange

from config_fastapi.config_fastapi import rabbit_router
from src.moralis.moralis_api import MoralisAPI
from src.core.register import RegisterContainer

moralis_exchange = RabbitExchange(name='moralis_exchange')


@rabbit_router.handle('get_native_transactions', exchange=moralis_exchange)
async def get_native_transactions(
        data: dict,
):
    moralis_api: MoralisAPI = RegisterContainer.moralis_container.moralis_api()
    limit: int = int(data.get('limit'))
    address: str = data.get('address')
    cursor: str = data.get('cursor')
    page: str = data.get('page')
    from_block: int = data.get('from_block')
    transactions_list = []
    while True:
        transactions_cursor = transactions_list[-1].get('cursor') if len(transactions_list) > 0 else None

        transactions = await moralis_api.get_native_transactions(address=address,
                                                                 limit=limit,
                                                                 cursor=transactions_cursor,
                                                                 page=page,
                                                                 from_block=from_block
                                                                 )

        transactions_list.append(transactions)

        if transactions_cursor is None and len(transactions_list) > 1:
            break
    return [transactions['result'] for transactions in transactions_list]
