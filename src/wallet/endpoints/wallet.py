from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from src.auth.endpoints.auth import user_auth
from src.wallet.containers import WalletContainer
from src.wallet.service.wallet import WalletService

wallet_router = APIRouter(tags=['wallet'])


@wallet_router.get(
    '/wallet/create/',

)
@inject
async def create_wallet(
        wallet_service: WalletService = Depends(Provide[WalletContainer.wallet_service])
):
    response = await wallet_service.create_wallet()
    return {'response': response}


@wallet_router.post(
    '/wallet/balance/',

)
@inject
async def get_balance(
        wallet_address: str,
        wallet_service: WalletService = Depends(Provide[WalletContainer.wallet_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),

):
    response = await wallet_service.get_balance(wallet_address)
    return {'response': response}


@wallet_router.post(
    '/wallet/send/',

)
@inject
async def send_transaction(
        from_address: str,
        to_address: str,
        wallet_service: WalletService = Depends(Provide[WalletContainer.wallet_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),

):
    response = await wallet_service.send_transaction(from_address, to_address)
    return {'response': response}
