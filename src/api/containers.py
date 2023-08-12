from dependency_injector import containers, providers
from config.settings import MORALIS_API_KEY
from src.api.moralis_api import MoralisAPI


class APIContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=[
        'src.users', 'src.auth', 'src.wallet', 'src.core', 'config', 'src.api'
    ]
    )
    moralis_api = providers.Singleton(MoralisAPI, api_key=MORALIS_API_KEY)
