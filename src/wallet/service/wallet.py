from typing import Iterator

import hexbytes
from fastapi import HTTPException
from eth_account import Account
import secrets

from hexbytes import HexBytes
from web3.datastructures import AttributeDict

from src.api.moralis_api import MoralisAPI
from src.api.web3_api import Web3API
from src.auth.dependencies.jwt_auth import decode_token
from src.boto3.services.boto3 import Boto3Service
from src.users.services.user import UserService
from src.wallet.models import Wallet, Asset, Transaction
from src.wallet.repositories.repository import WalletRepository
from src.wallet.schemas import AssetSchema


class WalletService:

    def __init__(self, wallet_repository: WalletRepository,
                 user_service: UserService,
                 moralis_api: MoralisAPI,
                 web3_api: Web3API,
                 boto3_service: Boto3Service,
                 ) -> None:
        self.wallet_repository = wallet_repository
        self.user_service = user_service
        self.moralis_api = moralis_api
        self.web3_api = web3_api
        self.boto3_service = boto3_service

    async def create_wallet(self, access_token: str, asset_id: int) -> Wallet:
        payload = decode_token(access_token)
        # get user
        if payload:
            user = await self.user_service.get_user_by_id(payload.get('user_id'))
        else:
            user = await self.user_service.get_user_by_id(1)

        # random string hex
        private = secrets.token_hex(32)

        private_key = "0x" + private

        # create account
        account = Account.from_key(private_key)

        return await self.wallet_repository.create_wallet(address=account.address, private_key=private_key,
                                                          user_id=user.id, asset_id=asset_id)

    async def get_balance(self, address: str) -> float:
        return await self.web3_api.get_balance(address)

    async def send_transaction(self, from_address: str, to_address: str, amount: float) -> str:
        sender_wallet = await self.wallet_repository.get_wallet(from_address)
        # gas_amount
        gas = 21000
        nonce = await self.web3_api.web3.eth.get_transaction_count(from_address)

        transaction = {
            'chainId': await self.web3_api.web3.eth.chain_id,
            'from': from_address,
            'to': to_address,
            'value': await self.web3_api.convert_ether_to_wei(amount),
            'nonce': nonce,
            'gasPrice': self.web3_api.web3.to_wei('50', 'gwei'),
            'gas': gas,
        }

        signed_transaction = await self.web3_api.sign_transaction(transaction=transaction,
                                                                  private_key=sender_wallet.private_key)

        transaction_hash = await self.web3_api.send_raw_transaction(signed_transaction=signed_transaction)

        db_transaction = await self.wallet_repository.create_transaction(
            transaction_hash=transaction_hash,
            from_address=from_address,
            to_address=to_address,
            value=amount,
        )
        return transaction_hash.hex()

    async def get_wallet_transactions(self, address: str, limit: int) -> dict:
        response = await self.moralis_api.get_native_transactions(address, limit)
        return response

    async def get_transaction_by_hash(self, transaction_hash: str) -> AttributeDict:
        response: AttributeDict = await self.web3_api.web3.eth.get_transaction(transaction_hash=transaction_hash)
        return response

    async def import_wallet(self, private_key: str, access_token: str) -> Wallet:
        account = Account.from_key(private_key)
        address = account.address
        balance = await self.get_balance(address)
        user = await self.user_service.profile(access_token)
        if balance and user:
            wallet = await self.wallet_repository.import_wallet(private_key, address, user_id=user.id)
            await self.wallet_repository.set_balance(balance, wallet.address)
            return wallet
        else:
            raise HTTPException(status_code=400, detail='Wallet exception')

    async def get_wallets_address_in_block(self, wallet_address: list) -> Iterator[str]:
        return await self.wallet_repository.get_wallets_address_in_block(wallet_address)

    async def get_transaction_receipt(self, transaction_hash: str) -> AttributeDict:
        return await self.web3_api.web3.eth.get_transaction_receipt(transaction_hash)

    async def get_transaction_by_id(self, transaction_id: int) -> Transaction:
        return await self.wallet_repository.get_transaction_by_id(transaction_id)
