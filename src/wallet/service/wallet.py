import hexbytes
from fastapi import HTTPException
from eth_account import Account
import secrets
from src.api.moralis_api import MoralisAPI
from src.api.web3_api import Web3API
from src.auth.dependencies.jwt_auth import decode_token
from src.users.services.user import UserService
from src.wallet.models import Wallet
from src.wallet.repositories.repository import WalletRepository


# TODO: Сделать через env

# https://sepolia-eth.w3node.com/30190b0446cdb3ae4e04547fb6c10cf78d0d2857d0d09983c1a386a5c5621ef6/api
# https://rpc.notadegen.com/sepolia


class WalletService:

    def __init__(self, wallet_repository: WalletRepository,
                 user_service: UserService,
                 moralis_api: MoralisAPI,
                 web3_api: Web3API,
                 ) -> None:
        self.wallet_repository = wallet_repository
        self.user_service = user_service
        self.moralis_api = moralis_api
        self.web3_api = web3_api

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

    async def get_balance(self, address: str) -> float:
        return self.web3_api.get_balance(address)

    async def send_transaction(self, from_address: str, to_address: str, amount: float) -> str:
        sender_wallet = await self.wallet_repository.get_wallet(from_address)
        gas_price = self.web3_api.web3.eth.gas_price
        # gas_amount
        gas = 2_000_000

        nonce = self.web3_api.web3.eth.get_transaction_count(from_address)
        transaction = {
            'chainId': self.web3_api.web3.eth.chain_id,
            'from': from_address,
            'to': to_address,
            'value': self.web3_api.convert_ether_to_wei(amount),
            'nonce': nonce,
            # 'gasPrice': gas_price,
            'gasPrice': self.web3_api.web3.to_wei('5', 'gwei'),
            'gas': gas,
        }

        signed_transaction = self.web3_api.sign_transaction(transaction=transaction,
                                                            private_key=sender_wallet.private_key)
        transaction = await self.wallet_repository.create_transaction(
            transaction_hash='0x7ad0c1ce025d211a13b2d2bab0feeadc657fd56deb1218709278ec73108c4154',
            from_address=from_address,
            to_address=to_address,
            value=amount,
        )
        block_data = self.web3_api.web3.eth.get_block(4073775)
        for transaction_block in block_data.transactions:
            if hexbytes.HexBytes(transaction_block).hex() == transaction.hash:
                print(await self.get_transaction_by_hash(transaction.hash))

        return transaction
        # transaction_hash = self.web3_api.send_raw_transaction(signed_transaction=signed_transaction)
        # return transaction_hash.hex()

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
