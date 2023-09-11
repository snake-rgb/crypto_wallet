from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from src.auth.dependencies import jwt_auth
from src.auth.endpoints.auth import user_auth
from src.core.register import RegisterContainer
from src.users.models import User
from src.users.services.user import UserService
from src.wallet.models import Wallet
from src.wallet.schemas import WalletSchema
from src.wallet.service.wallet import WalletService

wallet_router = APIRouter(tags=['wallet'])


@wallet_router.post(
    '/wallet/create/',

)
@inject
async def create_wallet(
        asset_id: int,
        wallet_service: WalletService = Depends(Provide[RegisterContainer.wallet_container.wallet_service]),
        user_service: UserService = Depends(Provide[RegisterContainer.user_container.user_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),
):
    payload: dict = jwt_auth.decode_token(bearer.credentials)
    # get user
    if payload:
        user: User = await user_service.get_user_by_id(payload.get('user_id'))
    else:
        user: User = await user_service.get_user_by_id(1)

    response: Wallet = await wallet_service.create_wallet(user.id, asset_id)
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
        transaction_hash: str,
        wallet_service: WalletService = Depends(Provide[RegisterContainer.wallet_container.wallet_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),
):
    response = await wallet_service.get_transaction_by_hash(transaction_hash=transaction_hash)
    return response


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
    '/wallet/send-transaction/',

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


@wallet_router.get(
    '/wallet/get-user-wallets/',

)
@inject
async def get_user_wallets(
        user_id: int,
        wallet_service: WalletService = Depends(Provide[RegisterContainer.wallet_container.wallet_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),

) -> dict:
    response = await wallet_service.get_user_wallets(user_id)
    wallets = [WalletSchema(
        id=wallet.id,
        address=wallet.address,
        balance=wallet.balance,
        asset_image=wallet.asset.image,
    ) for wallet in response]
    return {'wallets': wallets}
