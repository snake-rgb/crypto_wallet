from decimal import Decimal

from eth_account.datastructures import SignedTransaction
from eth_typing import BlockNumber
from fastapi import HTTPException
from hexbytes import HexBytes
from web3 import AsyncWeb3, AsyncHTTPProvider, WebsocketProviderV2
from web3.eth import AsyncEth
from web3.types import BlockData, Wei
from web3.exceptions import InsufficientData, InvalidTransaction


class Web3API:
    def __init__(self, http_provider_url: str, wss_provider_url: str) -> None:
        self.wss_provider_url = wss_provider_url
        self.web3 = AsyncWeb3(AsyncHTTPProvider(http_provider_url, request_kwargs={'timeout': 120}),
                              modules={'eth': (AsyncEth,)})
        self.web3_socket = AsyncWeb3(WebsocketProviderV2(
            self.wss_provider_url,
            {
                'max_size': 5 ** 20,
            }))

    async def get_balance(self, address: str) -> Wei:
        balance = await self.web3.eth.get_balance(address)
        return balance

    async def convert_ether_to_wei(self, amount: float) -> Wei:
        return self.web3.to_wei(amount, 'ether')

    async def convert_wei_to_ether(self, amount: float) -> Decimal:
        return self.web3.from_wei(amount, 'ether')

    async def sign_transaction(self, transaction: dict) -> dict:
        private_key: str = transaction.pop('private_key')
        signed_transaction: SignedTransaction = self.web3.eth.account.sign_transaction(transaction, private_key)
        return {
            'rawTransaction': signed_transaction.__getitem__(0).hex(),
            'hash': signed_transaction.__getitem__(1).hex(),
            'r': signed_transaction.__getitem__(2),
            's': signed_transaction.__getitem__(3),
            'v': signed_transaction.__getitem__(4),
        }

    async def send_raw_transaction(self, signed_transaction: dict) -> HexBytes:
        raw_transaction = await self.web3.eth.send_raw_transaction(signed_transaction.get('rawTransaction'))
        return raw_transaction

    async def get_block_latest(self) -> BlockData:
        return await self.web3_socket.eth.get_block('latest')

    async def get_block_number_latest(self) -> BlockNumber:
        return await self.web3_socket.eth.get_block_number()

    async def get_block_by_number(self, block_number: int) -> BlockData:
        async with AsyncWeb3.persistent_websocket(
                WebsocketProviderV2(self.wss_provider_url, websocket_kwargs={'max_size': 5 ** 20, })
        ) as web3:
            return await web3.eth.get_block(block_identifier=block_number, full_transactions=True)
