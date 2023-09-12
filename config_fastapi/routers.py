from fastapi import FastAPI
from src.auth.endpoints.auth import auth_router
from src.auth.views import auth_view_router
from src.chat.endpoints.chat import chat_router
from src.chat.views import chat_view_router
from src.ibay.endpoints.ibay import ibay_router
from src.users.endpoints.user_endpoints import register_router
from src.users.views import user_view_router
from src.wallet.endpoints.wallet import wallet_router


def init_routers(app: FastAPI) -> None:
    # API routers
    app.include_router(prefix='/api/v1', router=register_router)
    app.include_router(prefix='/api/v1', router=auth_router)
    app.include_router(prefix='/api/v1', router=wallet_router)
    app.include_router(prefix='/api/v1', router=ibay_router)
    app.include_router(prefix='/api/v1', router=chat_router)

    # VIEW routers
    app.include_router(router=user_view_router)
    app.include_router(router=auth_view_router)
    app.include_router(router=chat_view_router)
