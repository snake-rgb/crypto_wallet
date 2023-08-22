import logging
from propan.brokers.rabbit import RabbitExchange, ExchangeType
from config_socketio.config_socketio import socket_rabbit_router
from src.core.register import RegisterContainer
from src.parser.services.parser import ParserService
from src.parser.tasks import parse_block

redis = RegisterContainer.parser_container.redis()

socketio_exchange = RabbitExchange(name='socketio', type=ExchangeType.FANOUT)
logger = logging.getLogger(__name__)


@socket_rabbit_router.handle('last_block_event')
async def last_block_event(
        block_number: str,
) -> None:
    parser_service: ParserService = RegisterContainer.parser_container.parser_service()
    block_number: int = int(block_number)

    # block numbers from redis and web3
    redis_last_block_bytes: bytes = await redis.get('last_block_number')
    redis_last_block_number: int = int(redis_last_block_bytes.decode('utf-8'))
    print(f'{redis_last_block_number} - {block_number}')
    # block_number = 4137254
    # # create task for parse block
    # parse_block.apply_async(args=[4137254])
    while redis_last_block_number < block_number:
        parse_block.apply_async(args=[redis_last_block_number])
        redis_last_block_number += 1

    await redis.set('last_block_number', block_number)
