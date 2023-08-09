from fastapi import FastAPI
from src.auth.endpoints.auth import auth_router
from src.core.register import RegisterContainer
from src.users.endpoints.user_endpoints import register_router, user_rabbit_router
from src.wallet.endpoints.wallet import wallet_router


def create_app():
    container = RegisterContainer()
    db = container.core_container.db()
    db.create_database()

    # fast api
    fast_api_app = FastAPI(lifespan=user_rabbit_router.lifespan_context)

    fast_api_app.container = container
    fast_api_app.include_router(register_router)
    fast_api_app.include_router(auth_router)
    fast_api_app.include_router(user_rabbit_router)
    fast_api_app.include_router(wallet_router)
    return fast_api_app


app = create_app()
