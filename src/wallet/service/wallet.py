from typing import Callable
from sqlalchemy.orm import Session
from web3 import Web3, HTTPProvider
from eth_account import Account
import secrets

from src.wallet.repositories.repository import WalletRepository

# from config import settings

# w3 = Web3(HTTPProvider(settings.ETHEREUM_NODE_URL))

# TODO: Сделать через env

web3 = Web3(HTTPProvider(
    'https://sepolia-eth.w3node.com/30190b0446cdb3ae4e04547fb6c10cf78d0d2857d0d09983c1a386a5c5621ef6/api'))


# print(web3.eth.get_balance('0x9841b300b8853e47b7265dfF47FD831642e649e0'))
# print(web3.eth.get_balance('0xEd25b4F1608a5154E2F8c2e4521260D099f8B22c'))
# print(web3.eth.get_balance('0xEB47e3beA40816597A8214fc507B71C08A029630'))
# print("Latest Ethereum block number", web3.eth.get_block('latest'))


class WalletService:

    def __init__(self, wallet_repository: WalletRepository) -> None:
        self.wallet_repository = wallet_repository

    async def create_wallet(self):
        # random string hex
        private = secrets.token_hex(32)

        private_key = "0x" + private
        # create account
        account = Account.from_key(private_key)

        return await self.wallet_repository.create_wallet(address=account.address, private_key=private_key)

    async def get_balance(self, address: str) -> float:
        wallet = await self.wallet_repository.get_wallet(address)
        checksum_address = web3.to_checksum_address(wallet.address)
        balance = web3.eth.get_balance(checksum_address)
        return balance

    async def send_transaction(self, from_address: str, to_address: str) -> None:
        pass
