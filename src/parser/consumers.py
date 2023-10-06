from propan.brokers.rabbit import RabbitExchange

from config_fastapi.config_fastapi import rabbit_router
from src.core.register import RegisterContainer
from src.parser.services.parser import ParserService

parser_exchange = RabbitExchange(name='parser_exchange')


@rabbit_router.handle('start_parse', exchange=parser_exchange)
async def start_parse(
        block_number: str,
) -> None:
    parser_service: ParserService = RegisterContainer.parser_container.parser_service()
    block_number: int = int(block_number)
    await parser_service.start_parse(block_number=block_number)
