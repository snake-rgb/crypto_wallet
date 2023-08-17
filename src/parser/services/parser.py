from propan import RabbitBroker
from redis.client import Redis
from config import settings
from src.api.web3_api import Web3API


class ParserService:

    def __init__(self, web3_api: Web3API, redis_pool: Redis):
        self.parse_block_list = []
        self.web3_api = web3_api
        self.redis_pool = redis_pool

    async def get_block_by_number(self, block_number: int):
        block = await self.web3_api.get_block_by_number(block_number)
        self.parse_block_list.append(block)
        self.parse_block_list = list(set(self.parse_block_list))
        print(self.parse_block_list)
        return block
