import asyncio

from asgiref.sync import async_to_sync

from src.core.register import RegisterContainer
from src.parser.services.parser import ParserService

celery = RegisterContainer.celery()


@celery.task
def parse_block(block_number: int):
    parser_service: ParserService = RegisterContainer.parser_container.parser_service()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(parser_service.get_block_by_number(block_number))
    return {'status': 'success'}
