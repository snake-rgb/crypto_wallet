from typing import Iterator
from propan import RabbitBroker
from redis.client import Redis
from web3.datastructures import AttributeDict
from web3.types import BlockData

from config import settings
from src.api.web3_api import Web3API
from src.wallet.service.wallet import WalletService


class ParserService:

    def __init__(self, web3_api: Web3API, redis_pool: Redis, wallet_service: WalletService):
        self.web3_api = web3_api
        self.redis_pool = redis_pool
        self.wallet_service = wallet_service

    async def get_block_by_number(self, block_number: int) -> AttributeDict:
        block = await self.web3_api.get_block_by_number(block_number)
        await self.parse_block(block['transactions'])
        return block

    async def parse_block(self, transactions: Iterator[AttributeDict]):
        print('parse_block')
        # transactions_data = [[tx['hash'].hex(), tx.get('from'), tx.get('to')] for tx in transactions]
        # transactions_wallets_address_from: list = [tx.get('from') for tx in transactions]
        # transactions_wallets_address_to: list = [tx.get('to') for tx in transactions]

        # wallets_address = await self.wallet_service.get_wallets_address_in_block(transactions_wallets_address_to)
        # print(transactions_wallets_address_to)
        # async with RabbitBroker(settings.RABBITMQ_URL) as broker:
        #     await broker.publish(f'{transactions_hashes}', queue='parse_finished_event')
