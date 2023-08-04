from fastapi import FastAPI
from src.core.containers import CoreContainer


def create_app():
    container = CoreContainer()
    db = container.db()
    db.create_database()
    # fast api
    fast_api_app = FastAPI()

    fast_api_app.container = container
    return fast_api_app


app = create_app()
