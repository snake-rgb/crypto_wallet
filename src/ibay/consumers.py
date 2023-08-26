from config_socketio.config_socketio import socket_rabbit_router


@socket_rabbit_router.handle('parse_finished')
async def parse_finished(
        msg
):
    print(f'msg - ', msg)
