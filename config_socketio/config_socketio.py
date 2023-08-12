import socketio
from config.settings import SOCKET_IO_ORIGINS

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=SOCKET_IO_ORIGINS)
socket_app = socketio.ASGIApp(sio, )


@sio.on("connect")
async def connect(sid, environ):
    print(f"Client {sid} connected")


@sio.on("disconnect")
async def disconnect(sid):
    print(f"Client {sid} disconnected")


@sio.on("message")
async def message_from_client(sid, data):
    print(f"Received message from client {sid}: {data}")
    await sio.emit("message_from_server", f"Server received: {data}", room=sid)
