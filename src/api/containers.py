from dependency_injector import containers, providers
from config.settings import MORALIS_API_KEY, HTTP_PROVIDER_URL, WSS_PROVIDER_URL
from src.api.moralis_api import MoralisAPI
from src.api.web3_api import Web3API


class APIContainer(containers.DeclarativeContainer):
    moralis_api = providers.Singleton(MoralisAPI, api_key=MORALIS_API_KEY)
    web3_api = providers.Singleton(Web3API, http_provider_url=HTTP_PROVIDER_URL, wss_provider_url=WSS_PROVIDER_URL)
