from dependency_injector import containers, providers
from config.settings import HTTP_PROVIDER_URL, WSS_PROVIDER_URL
from src.web3.web3_api import Web3API


class Web3Container(containers.DeclarativeContainer):
    web3_api = providers.Singleton(Web3API, http_provider_url=HTTP_PROVIDER_URL, wss_provider_url=WSS_PROVIDER_URL)
