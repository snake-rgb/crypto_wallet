from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import HTTPAuthorizationCredentials

from src.auth.dependencies import jwt_auth
from src.auth.dependencies.jwt_auth import decode_token
from src.auth.endpoints.auth import user_auth
from src.core.register import RegisterContainer
from src.users.models import User
from src.users.services.user import UserService
from src.wallet.models import Wallet
from src.wallet.schemas import WalletSchema, TransactionSchema
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

    wallet: Wallet = await wallet_service.create_wallet(user.id, asset_id)
    return {'wallet': wallet}


@wallet_router.get(
    '/wallet/transactions/',

)
@inject
async def get_wallet_transactions(
        address: str,
        request: Request,
        limit: int | None = 100,
        cursor: str | None = None,
        page: int | None = None,
        wallet_service: WalletService = Depends(Provide[RegisterContainer.wallet_container.wallet_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),
):
    address = address.lower()
    latest_transaction = await wallet_service.get_latest_transaction_by_wallet(address)

    if latest_transaction:
        block_data = await wallet_service.get_transaction_by_hash(latest_transaction.hash)
        from_block = block_data.get('blockNumber') if block_data is not None else None
    else:
        from_block = None

    await wallet_service.get_wallet_transactions(address=address, limit=limit, cursor=cursor, page=page,
                                                 from_block=from_block)
    transactions_db = await wallet_service.get_wallet_transactions_from_db(address)
    return {
        'draw': request.query_params.get('draw'),
        "recordsTotal": len(transactions_db),
        "recordsFiltered": len(transactions_db),
        'data': transactions_db,
    }


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
        transaction_schema: TransactionSchema,
        wallet_service: WalletService = Depends(Provide[RegisterContainer.wallet_container.wallet_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),

):
    transaction = await wallet_service.send_transaction(
        from_address=transaction_schema.from_address,
        to_address=transaction_schema.to_address,
        amount=transaction_schema.amount,
    )
    return {'transaction': transaction}


@wallet_router.post(
    '/wallet/import/',

)
@inject
async def import_wallet(
        private_key: str,
        wallet_service: WalletService = Depends(Provide[RegisterContainer.wallet_container.wallet_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),

):
    try:
        wallet: Wallet = await wallet_service.import_wallet(private_key, bearer.credentials)
        return {'wallet': wallet}
    except Exception as error:
        print(error)


@wallet_router.get(
    '/wallet/get-user-wallets/',

)
@inject
async def get_user_wallets(
        wallet_service: WalletService = Depends(Provide[RegisterContainer.wallet_container.wallet_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),

) -> dict:
    payload = decode_token(bearer.credentials)
    user_id: int = payload.get('user_id')
    response = await wallet_service.get_user_wallets(user_id)
    wallets = [WalletSchema(
        id=wallet.id,
        address=wallet.address,
        balance=float(wallet.balance).__round__(3),
        asset_image=wallet.asset.image,
    ) for wallet in response]
    return {'wallets': wallets}
