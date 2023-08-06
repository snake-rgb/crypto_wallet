from fastapi import FastAPI
from propan.fastapi import RabbitRouter
from config import settings
from src.auth.endpoints.auth import auth_router
from src.core.register import RegisterContainer
from src.users.endpoints.user_endpoints import register_router
from src.users.tasks import sample_task
rabbit_router = RabbitRouter(settings.RABBITMQ_URL)


@rabbit_router.event('helloworld')
async def helloworld():
    print('hello world from broker')


@rabbit_router.get('/my_test/')
async def my_test():
    sample_task.apply_async()
    await rabbit_router.broker.publish("Hello, Rabbit!", "helloworld")


def create_app():
    container = RegisterContainer()
    db = container.core_container.db()
    db.create_database()

    # fast api
    fast_api_app = FastAPI(lifespan=rabbit_router.lifespan_context)

    fast_api_app.container = container
    fast_api_app.include_router(register_router, tags=['User'])
    fast_api_app.include_router(auth_router, tags=['Auth'])
    fast_api_app.include_router(rabbit_router)
    return fast_api_app


app = create_app()
