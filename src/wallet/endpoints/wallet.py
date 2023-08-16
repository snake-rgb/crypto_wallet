from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from propan import Depends as PropanDepends
from web3.datastructures import AttributeDict

from config_socketio.config_socketio import socket_rabbit_router
from src.auth.endpoints.auth import user_auth
from src.core.register import RegisterContainer
from src.wallet.service.wallet import WalletService

wallet_router = APIRouter(tags=['wallet'])


@socket_rabbit_router.handle('event1', exchange='default')
@inject
async def event(
        body,
        user_service=PropanDepends(Provide[RegisterContainer.user_container.user_service])
):
    # TODO: Прокинуть сервис ?
    pass
    # print(await user_service.dependency().get_user())
    # print(await wallet_service.get_wallet_transactions('0x9841b300b8853e47b7265dfF47FD831642e649e0', limit=10))


@wallet_router.get(
    '/wallet/create/',

)
@inject
async def create_wallet(
        wallet_service: WalletService = Depends(Provide[RegisterContainer.wallet_container.wallet_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),
):
    response = await wallet_service.create_wallet(bearer.credentials)
    return {'response': response}


@wallet_router.post(
    '/wallet/transactions/',

)
@inject
async def get_wallet_transactions(
        address: str,
        limit: int | None = 10,
        wallet_service: WalletService = Depends(Provide[RegisterContainer.wallet_container.wallet_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),
):
    response = await wallet_service.get_wallet_transactions(address=address, limit=limit)
    return {'response': response}


@wallet_router.post(
    '/wallet/transaction/by_hash/',
)
@inject
async def get_transaction_by_hash(
        transaction_hase: str,
        wallet_service: WalletService = Depends(Provide[RegisterContainer.wallet_container.wallet_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),
):
    response = await wallet_service.get_transaction_by_hash(transaction_hase=transaction_hase)
    return {'response': response}


@wallet_router.post(
    '/wallet/balance/',

)
@inject
async def get_balance(
        wallet_address: str,
        wallet_service: WalletService = Depends(Provide[RegisterContainer.wallet_container.wallet_service]),
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
        amount: float,
        wallet_service: WalletService = Depends(Provide[RegisterContainer.wallet_container.wallet_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),

):
    response = await wallet_service.send_transaction(from_address=from_address,
                                                     to_address=to_address,
                                                     amount=amount,
                                                     )
    return {'response': response}


@wallet_router.post(
    '/wallet/import/',

)
@inject
async def import_wallet(
        private_key: str,
        wallet_service: WalletService = Depends(Provide[RegisterContainer.wallet_container.wallet_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),

):
    response = await wallet_service.import_wallet(private_key, bearer.credentials)
    return {'response': response}
