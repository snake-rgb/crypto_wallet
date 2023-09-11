import asyncio
from src.core.register import RegisterContainer
from src.parser.services.parser import ParserService

celery = RegisterContainer.celery()


@celery.task(bind=True, max_retries=3)
def parse_block(self, block_number: int):
    try:
        parser_service: ParserService = RegisterContainer.parser_container.parser_service()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(parser_service.parse_block(block_number))
        return {
            'block_number': block_number,
        }

    except TimeoutError:
        self.retry(countdown=3 ** self.request.retries)
