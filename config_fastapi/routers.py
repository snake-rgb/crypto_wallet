from fastapi import FastAPI
from src.auth.endpoints.auth import auth_router
from src.users.endpoints.user_endpoints import register_router
from src.wallet.endpoints.wallet import wallet_router


def init_routers(app: FastAPI) -> None:
    app.include_router(register_router)
    app.include_router(auth_router)
    app.include_router(wallet_router)
