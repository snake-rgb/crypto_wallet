from fastapi import FastAPI
from src.users.containers import UserContainer
from src.users.endpoints.register import register_router


def create_app():
    container = UserContainer()

    # fast api
    fast_api_app = FastAPI()
    fast_api_app.container = container
    fast_api_app.include_router(register_router)
    return fast_api_app


app = create_app()
