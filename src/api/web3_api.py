from eth_account.datastructures import SignedTransaction
from hexbytes import HexBytes
from web3 import Web3, HTTPProvider, WebsocketProvider, AsyncWeb3
from web3.eth import AsyncEth


class Web3API:
    def __init__(self, http_provider_url: str, wss_provider_url: str) -> None:
        self.http_provider_url = http_provider_url
        self.wss_provider_url = wss_provider_url
        self.web3 = Web3(HTTPProvider(self.http_provider_url))
        self.web3_socket = Web3(WebsocketProvider(self.wss_provider_url))

    def get_balance(self, address: str) -> float:
        balance = self.web3.eth.get_balance(address)
        ether_balance = self.web3.from_wei(balance, 'ether')
        return ether_balance

    def convert_ether_to_wei(self, amount) -> float:
        return self.web3.to_wei(amount, 'ether')

    def sign_transaction(self, transaction: dict, private_key: str) -> SignedTransaction:
        return self.web3.eth.account.sign_transaction(transaction, private_key)

    def send_raw_transaction(self, signed_transaction: SignedTransaction) -> HexBytes:
        return self.web3.eth.send_raw_transaction(signed_transaction.rawTransaction)

    def get_block_latest(self):
        return self.web3_socket.eth.get_block('latest')
