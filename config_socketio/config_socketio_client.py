import asyncio
import socketio

# Создаем экземпляр Socket.IO AsyncClient
socketio_client = socketio.AsyncClient()


# Обработчик события "connect"
@socketio_client.on('connect')
async def on_connect():
    print('Подключено к чату')


async def main():
    # Подключаемся к серверу Socket.IO
    await socketio_client.connect('http://localhost:8001')

    # Ожидаем подключения
    await socketio_client.wait()


# Запускаем асинхронный цикл событий
if __name__ == '__main__':
    asyncio.run(main())
