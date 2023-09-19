from datetime import datetime

from hexbytes import HexBytes
from propan.brokers.rabbit import RabbitExchange
from config_socketio.config_socketio import socket_rabbit_router
from src.core.register import RegisterContainer
from src.wallet.models import Transaction
from src.wallet.service.wallet import WalletService

wallet_exchange = RabbitExchange(name='wallet_exchange')


@socket_rabbit_router.handle('send_transaction', exchange=wallet_exchange)
async def send_transaction(
        data,
):
    wallet_service: WalletService = RegisterContainer.wallet_container.wallet_service()
    await wallet_service.buy_product(data)


@socket_rabbit_router.handle('order_refund', exchange=wallet_exchange)
async def order_refund(
        data,
):
    wallet_service: WalletService = RegisterContainer.wallet_container.wallet_service()
    await wallet_service.order_refund(data)


@socket_rabbit_router.handle('get_wallets_address_in_block', exchange=wallet_exchange)
async def get_wallets_address_in_block(
        data,
):
    wallet_service: WalletService = RegisterContainer.wallet_container.wallet_service()
    return await wallet_service.get_wallets_address_in_block(data.get('wallet_address'))


@socket_rabbit_router.handle('create_transaction', exchange=wallet_exchange)
async def create_transaction(
        data,
):
    wallet_service: WalletService = RegisterContainer.wallet_container.wallet_service()
    date_string = data.get('age')
    date_format = '%Y-%m-%dT%H:%M:%S'
    age = datetime.strptime(date_string, date_format)
    transaction: Transaction = await wallet_service.create_transaction(
        transaction_hash=data.get('transaction_hash'),
        from_address=data.get('from_address'),
        to_address=data.get('to_address'),
        status=data.get('status'),
        value=data.get('value'),
        fee=data.get('fee'),
        age=age,
    )

    return {
        'transaction_hash': transaction.hash,
        'from_address': transaction.from_address,
        'to_address': transaction.to_address,
        'status': transaction.status,
        'value': transaction.value,
        'fee': transaction.fee,
        'age': transaction.age,
    }


@socket_rabbit_router.handle('change_balance', exchange=wallet_exchange)
async def change_balance(
        data,
):
    wallet_service: WalletService = RegisterContainer.wallet_container.wallet_service()
    await wallet_service.change_balance(
        address=data.get('address'),
        value=data.get('value'),
        operation_type=data.get('operation_type'),
    )


@socket_rabbit_router.handle('create_transaction_bulk', exchange=wallet_exchange)
async def create_transaction_bulk(
        data,
):
    wallet_service: WalletService = RegisterContainer.wallet_container.wallet_service()
    await wallet_service.create_transaction_bulk(data.get('transactions'))
