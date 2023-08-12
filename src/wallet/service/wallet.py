from typing import Callable
import httpx
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from web3 import Web3, HTTPProvider
from eth_account import Account
import secrets

from src.api.moralis_api import MoralisAPI
from src.auth.dependencies.jwt_auth import decode_token
from src.users.services.user import UserService
from src.wallet.models import Wallet
from src.wallet.repositories.repository import WalletRepository

# TODO: Сделать через env

# https://sepolia-eth.w3node.com/30190b0446cdb3ae4e04547fb6c10cf78d0d2857d0d09983c1a386a5c5621ef6/api
# https://rpc.notadegen.com/sepolia
web3 = Web3(HTTPProvider(
    'https://rpc.notadegen.com/sepolia'))


class WalletService:

    def __init__(self, wallet_repository: WalletRepository, user_service: UserService, moralis_api: MoralisAPI) -> None:
        self.wallet_repository = wallet_repository
        self.user_service = user_service
        self.moralis_api = moralis_api

    async def create_wallet(self, access_token) -> Wallet:
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
                                                          user_id=user.id)

    @staticmethod
    async def get_balance(address: str) -> float:
        checksum_address = web3.to_checksum_address(address)
        balance = web3.eth.get_balance(checksum_address)
        balance = web3.from_wei(balance, 'ether')
        return balance

    async def send_transaction(self, from_address: str, to_address: str, amount: float) -> str:
        sender_wallet = await self.wallet_repository.get_wallet(from_address)
        gas_price = web3.eth.gas_price
        # gas_amount
        gas = 2_000_000

        nonce = web3.eth.get_transaction_count(from_address)
        transaction = {
            'chainId': web3.eth.chain_id,
            'from': from_address,
            'to': to_address,
            'value': int(web3.to_wei(amount, 'ether')),
            'nonce': nonce,
            'gasPrice': gas_price,
            'gas': gas,
        }
        signed_txn = web3.eth.account.sign_transaction(transaction, sender_wallet.private_key)
        transaction_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return transaction_hash.hex()

    async def get_wallet_transactions(self, address: str, limit: int) -> dict:
        response = await self.moralis_api.get_native_transactions(address, limit)
        return response

    async def get_transaction_by_hash(self, transaction_hase: str) -> dict:
        response = await self.moralis_api.get_transaction_by_hash(transaction_hase=transaction_hase)
        return response

    async def import_wallet(self, private_key: str, access_token: str) -> Wallet:
        account = Account.from_key(private_key)
        address = account.address
        balance = await self.get_balance(address)
        user = await self.user_service.profile(access_token)

        if balance:
            wallet = await self.wallet_repository.import_wallet(private_key, address, user_id=user.id)
            await self.wallet_repository.set_balance(balance, wallet.address)
            return wallet
        else:
            raise HTTPException(status_code=400, detail='Wallet exception')
