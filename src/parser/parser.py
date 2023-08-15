from src.api.web3_api import Web3API


class ParserService:
    def __init__(self, web3_api: Web3API):
        self.web3_api = web3_api

    def get_block_latest(self):
        self.web3_api.get_block_latest()
