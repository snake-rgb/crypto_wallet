import datetime
import time
from decimal import getcontext
from aioredis import Redis
from celery import Celery
from propan import RabbitBroker
from web3.datastructures import AttributeDict
from web3.types import BlockData
from config import settings
from src.wallet.models import Transaction


class ParserService:
    def __init__(self, celery: Celery, redis: Redis):
        self.celery = celery
        self.redis = redis

    # TODO: сделать bulk update для транзакций
    async def parse_block(self, block_number: int):
        start_timer = time.perf_counter()
        block: dict = await self.get_block_data(block_number)

        # transaction age
        timestamp: int = block['timestamp']
        age = datetime.datetime.fromtimestamp(timestamp)
        # transactions from block
        transactions: list[dict] = block['transactions']

        wallets_address_in_transactions: list = [tx[key] for tx in transactions for key in ('from', 'to') if
                                                 key in tx]

        wallets_address = await self.get_wallets_address_from_db(wallets_address_in_transactions)

        # Get transactions hash list
        transactions_hash: set = set(
            [transaction.get('hash') for transaction in transactions
             if (transaction.get('from') is not None and transaction.get('from') in wallets_address)
             or (transaction.get('to') is not None and transaction.get('to') in wallets_address)])

        # get transaction data
        new_transactions: list[AttributeDict] = [tx for tx in transactions if tx.get('hash') in transactions_hash]

        order_transactions: list[Transaction] = []

        # parse transaction
        for transaction in new_transactions:
            transaction_receipt = await self.get_transaction_receipt(transaction_hash=transaction.get('hash'))

            # set Decimal precision
            getcontext().prec = 18
            # eth fee
            fee: float = (transaction.get('gas') * transaction.get('gasPrice')) / (10 ** 18)
            # eth amount
            amount: float = transaction.get('value') / (10 ** 18)

            db_transaction = await self.create_transaction(
                transaction_hash=transaction.get('hash'),
                from_address=transaction.get('from'),
                to_address=transaction.get('to'),
                value=amount,
                age=age,
                status=transaction_receipt.get('status'),
                fee=fee,
            )

            print(f'hash - {db_transaction.get("transaction_hash")}, status - {db_transaction.get("status")}')

            order_transactions.append(db_transaction)
            if transaction_receipt.get('status'):
                await self.change_balance(
                    address=transaction.get('from'),
                    value=amount + fee,
                    operation_type='subtract'
                )
                await self.change_balance(
                    address=transaction.get('to'),
                    value=amount,
                    operation_type='add'
                )

            # TODO: Make method from this part
            async with RabbitBroker(settings.RABBITMQ_URL) as broker:
                await broker.publish(
                    [{'hash': tx.get("transaction_hash"), 'status': tx.get("status")} for tx in order_transactions],
                    queue='check_orders_status',
                    exchange='ibay_exchange')

            end_timer = time.perf_counter()
            execution_time = end_timer - start_timer
            return execution_time

    async def start_parse(self, block_number: int):
        # block numbers from redis and web3
        redis_last_block_bytes: bytes = await self.redis.get('last_block_number')
        redis_last_block_number: int = int(redis_last_block_bytes.decode('utf-8'))
        while redis_last_block_number < block_number:
            # run task
            result = self.celery.send_task('src.parser.tasks.parse_block', args=[redis_last_block_number])
            redis_last_block_number += 1
        await self.redis.set('last_block_number', block_number)

    @staticmethod
    async def get_wallets_address_from_db(wallets_address: list[str]) -> list[str]:
        # Get wallets in block (saved in db)
        async with RabbitBroker(settings.RABBITMQ_URL) as broker:
            wallets_address: list = await broker.publish(
                {
                    'wallet_address': wallets_address
                },
                queue='get_wallets_address_in_block',
                exchange='wallet_exchange',
                callback=True)
            return wallets_address

    @staticmethod
    async def get_block_data(block_number: int) -> dict:
        async with RabbitBroker(settings.RABBITMQ_URL) as broker:
            block = await broker.publish(
                {
                    'block_number': block_number
                },
                queue='get_block_by_number',
                exchange='web3_exchange',
                callback=True)
            return block

    @staticmethod
    async def get_transaction_receipt(transaction_hash: str) -> dict:
        async with RabbitBroker(settings.RABBITMQ_URL) as broker:
            transaction_receipt: dict = await broker.publish(
                {
                    'transaction_hash': transaction_hash
                },
                queue='get_transaction_receipt',
                exchange='web3_exchange',
                callback=True)
            return transaction_receipt

    @staticmethod
    async def create_transaction(
            transaction_hash: str,
            from_address: str,
            to_address: str,
            value: float,
            age: datetime.datetime,
            status: str,
            fee: float
    ) -> dict:
        async with RabbitBroker(settings.RABBITMQ_URL) as broker:
            db_transaction: dict = await broker.publish(
                {
                    'transaction_hash': transaction_hash,
                    'from_address': from_address,
                    'to_address': to_address,
                    'value': value,
                    'age': age,
                    'status': status,
                    'fee': fee,
                },
                queue='create_transaction',
                exchange='wallet_exchange',
                callback=True
            )
            return db_transaction

    @staticmethod
    async def change_balance(
            address: str,
            value: float,
            operation_type: str,
    ) -> None:
        async with RabbitBroker(settings.RABBITMQ_URL) as broker:
            await broker.publish(
                {
                    'address': address,
                    'value': value,
                    'operation_type': operation_type,
                },
                queue='change_balance',
                exchange='wallet_exchange',
                callback=True)
