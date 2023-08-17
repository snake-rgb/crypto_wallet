from config_socketio.config_socketio import socket_rabbit_router
from src.core.register import RegisterContainer
from src.parser.services.parser import ParserService


@socket_rabbit_router.handle('last_block_event', exchange='default')
async def last_block_event(
        msg,
):
    parse_service: ParserService = RegisterContainer.parser_container.parser_service()
    print(msg)
    await parse_service.get_block_by_number(int(msg))


@socket_rabbit_router.handle('event1', exchange='default')
async def event(
        msg,
):
    pass
