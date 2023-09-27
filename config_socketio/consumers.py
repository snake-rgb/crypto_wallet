from propan.brokers.rabbit import RabbitExchange

from config_socketio.config_socketio import socket_rabbit_router, sio

socketio_exchange = RabbitExchange(name='socketio_exchange')


@socket_rabbit_router.handle('receive_transaction', exchange=socketio_exchange)
async def receive_transaction(
        data,
):
    await sio.emit('receive_transaction', data, room=data.get("user_id"))


@socket_rabbit_router.handle('order_status', exchange=socketio_exchange)
async def order_status(
        data,
):
    await sio.emit('order_status', data, room=data.get("user_id"))


@socket_rabbit_router.handle('create_order', exchange=socketio_exchange)
async def create_order(
        data,
):

    await sio.emit('create_order', data, room=data.get("user_id"))
