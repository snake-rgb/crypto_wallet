from typing import Callable
import httpx
from web3 import Web3, HTTPProvider
from eth_account import Account
import secrets

from src.auth.dependencies.jwt_auth import decode_token
from src.users.services.user import UserService
from src.wallet.repositories.repository import WalletRepository

# from moralis import evm_api

# from config import settings

# w3 = Web3(HTTPProvider(settings.ETHEREUM_NODE_URL))

# TODO: Сделать через env
api_key = ('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6ImNkNDM4NmQ'
           'zLTU5MzAtNGU1YS04NDhkLTUxODk2MTBlNDYzMCIsIm9yZ0lkIjoiMzUyMzIzIiwi'
           'dXNlcklkIjoiMzYyMTI3IiwidHlwZUlkIjoiYmM1YzA2ZmQtYjQzNS00MzA4LTkyM2E'
           'tOThlNWQwMmU5OGI4IiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE2OTE2MDAyNjEsImV4'
           'cCI6NDg0NzM2MDI2MX0.OVg4cwZ3zy7UejX2dENEeg8uiKtQRxBUzgak-5yfzU0')

web3 = Web3(HTTPProvider(
    'https://sepolia-eth.w3node.com/30190b0446cdb3ae4e04547fb6c10cf78d0d2857d0d09983c1a386a5c5621ef6/api'))


# print("Latest Ethereum block number", web3.eth.get_block('latest'))


class WalletService:

    def __init__(self, wallet_repository: WalletRepository, user_service: UserService) -> None:
        self.wallet_repository = wallet_repository
        self.user_service = user_service

    async def create_wallet(self, access_token):
        payload = decode_token(access_token)
        # get user
        if payload:
            user = await self.user_service.user_repository.get_by_id(payload.get('user_id'))
        else:
            user = await self.user_service.user_repository.get_by_id(1)

        # random string hex
        private = secrets.token_hex(32)

        private_key = "0x" + private

        # create account
        account = Account.from_key(private_key)

        return await self.wallet_repository.create_wallet(address=account.address, private_key=private_key,
                                                          user_id=user.id)

    async def get_balance(self, address: str) -> float:
        wallet = await self.wallet_repository.get_wallet(address)
        checksum_address = web3.to_checksum_address(wallet.address)
        balance = web3.eth.get_balance(checksum_address)
        return balance

    async def send_transaction(self, from_address: str, to_address: str) -> None:
        pass

    async def get_wallet_transactions(self, address: str):
        wallet = await self.wallet_repository.get_wallet(address)
        return await fetch_transactions(wallet.address)

    async def import_wallet(self, private_key: str):
        account = Account.from_key(private_key)
        address = account.address
        wallet = await self.wallet_repository.import_wallet(private_key, address)
        balance = await self.get_balance(wallet.address)
        balance = web3.from_wei(balance, 'ether')
        wallet = await self.wallet_repository.set_balance(balance, wallet.address)
        return wallet


# TODO: Переместить этот метод в get_wallet_transactions либо репозиторий
async def fetch_transactions(address: str):
    moralis_api_key = api_key

    url = f'https://deep-index.moralis.io/api/v2/{address}/balance?chain=sepolia'
    headers = {
        "X-API-Key": moralis_api_key
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            transactions_data = response.json()
            return transactions_data
        else:
            print("Ошибка при запросе к Moralis API:", response.status_code)
            return None
