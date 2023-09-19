from dependency_injector import containers, providers
from config.settings import MORALIS_API_KEY
from src.moralis.moralis_api import MoralisAPI


class MoralisContainer(containers.DeclarativeContainer):
    moralis_api = providers.Singleton(MoralisAPI, api_key=MORALIS_API_KEY)
