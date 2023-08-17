from eth_account.datastructures import SignedTransaction
from hexbytes import HexBytes
from web3 import Web3, WebsocketProvider, AsyncWeb3, AsyncHTTPProvider
from web3.eth import AsyncEth


class Web3API:
    def __init__(self, http_provider_url: str, wss_provider_url: str) -> None:
        self.http_provider_url = http_provider_url
        self.wss_provider_url = wss_provider_url
        self.web3 = AsyncWeb3(AsyncHTTPProvider(self.http_provider_url), modules={'eth': (AsyncEth,)})
        self.web3_socket = Web3(WebsocketProvider(self.wss_provider_url))

    async def get_balance(self, address: str) -> float:
        balance = await self.web3.eth.get_balance(address)
        return balance

    async def convert_ether_to_wei(self, amount) -> float:
        return self.web3.to_wei(amount, 'ether')

    async def sign_transaction(self, transaction: dict, private_key: str) -> SignedTransaction:
        return self.web3.eth.account.sign_transaction(transaction, private_key)

    async def send_raw_transaction(self, signed_transaction) -> HexBytes:
        return await self.web3.eth.send_raw_transaction(signed_transaction.rawTransaction)

    async def get_block_latest(self):
        return self.web3_socket.eth.get_block('latest')

    async def get_block_number_latest(self):
        return self.web3_socket.eth.get_block_number()

    async def get_block_by_number(self, block_number: int):
        return self.web3_socket.eth.get_block(block_number, full_transactions=True)
