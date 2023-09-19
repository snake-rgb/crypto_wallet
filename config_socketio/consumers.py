from propan.brokers.rabbit import RabbitExchange

from config_socketio.config_socketio import socket_rabbit_router, sio

socketio_exchange = RabbitExchange(name='socketio_exchange')


@socket_rabbit_router.handle('receive_transaction', exchange=socketio_exchange)
async def receive_transaction(
        data,
):
    await sio.emit('receive_transaction', data, room=data.get("user_id"))
