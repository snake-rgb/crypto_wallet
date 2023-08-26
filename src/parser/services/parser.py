import datetime
import time
from decimal import Decimal, getcontext
from typing import Iterator, Sequence
from propan import RabbitBroker
from redis.client import Redis
from web3.datastructures import AttributeDict
from web3.types import BlockData
from config import settings
from src.api.web3_api import Web3API
from src.wallet.models import Transaction
from src.wallet.service.wallet import WalletService


class ParserService:

    def __init__(self, web3_api: Web3API, redis_pool: Redis, wallet_service: WalletService):
        self.web3_api = web3_api
        self.redis_pool = redis_pool
        self.wallet_service = wallet_service

    async def parse_block(self, block_number: int):
        tm1 = time.perf_counter()
        block: BlockData = await self.web3_api.get_block_by_number(block_number)
        # transaction age
        timestamp: int = block['timestamp']
        age = datetime.datetime.fromtimestamp(timestamp)

        transactions: list[AttributeDict] = block['transactions']

        transactions_data: list[dict] = [{'hash': tx['hash'].hex(), 'from': tx.get('from'), 'to': tx.get('to')} for tx
                                         in
                                         transactions]

        wallets_address_in_transactions: list = [tx[key] for tx in transactions for key in ('from', 'to') if key in tx]

        # Get wallets in block (saved in db)
        wallets_address: list = list(
            set(await self.wallet_service.get_wallets_address_in_block(
                wallets_address_in_transactions)))

        # Get transactions hash list
        transactions_hash: set = set(
            [transaction.get('hash') for transaction in transactions
             if (transaction.get('from') is not None and transaction.get('from') in wallets_address)
             or (transaction.get('to') is not None and transaction.get('to') in wallets_address)])

        # get transaction data
        new_transactions: list[AttributeDict] = [tx for tx in transactions if tx.get('hash') in transactions_hash]
        print(transactions_hash)
        # parse transaction
        for transaction in new_transactions:
            transaction_receipt: AttributeDict = await self.wallet_service.get_transaction_receipt(
                transaction.get('hash'))
            # set Decimal precision
            getcontext().prec = 18
            # eth fee
            fee: float = (transaction.get('gas') * transaction.get('gasPrice')) / (10 ** 18)
            # eth amount
            amount: float = transaction.get('value') / (10 ** 18)

            info = f'fee - {fee}\n amount - {amount}\n'
            # print(info)

            db_transaction: Transaction = await self.wallet_service.wallet_repository.create_transaction(
                transaction_hash=transaction.get('hash'),
                from_address=transaction.get('from'),
                to_address=transaction.get('to'),
                value=amount,
                age=age,
                status=transaction_receipt.get('status'),
                # convert from wei for db
                fee=fee,
            )

            if db_transaction.status:
                await self.wallet_service.wallet_repository.change_balance(
                    value=amount + fee,
                    address=transaction.get('from'),
                    operation_type='subtract')
                await self.wallet_service.wallet_repository.change_balance(
                    value=amount,
                    address=transaction.get('to'),
                    operation_type='add')
            # print(transaction)
            async with RabbitBroker(settings.RABBITMQ_URL) as broker:
                await broker.publish({'test': [tx.get('hash').hex() for tx in new_transactions]},
                                     queue='parse_finished')
            tm2 = time.perf_counter()
            execution_time = tm2 - tm1
            return execution_time
