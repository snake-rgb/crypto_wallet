from dependency_injector import containers, providers
from src.wallet.repositories.repository import WalletRepository
from src.wallet.service.wallet import WalletService


class WalletContainer(containers.DeclarativeContainer):
    session = providers.Dependency()
    user_service = providers.Dependency()
    moralis_api = providers.Dependency()
    web3_api = providers.Dependency()
    # repository
    wallet_repository = providers.Factory(WalletRepository, session)

    # services
    wallet_service = providers.Factory(WalletService, wallet_repository, user_service, moralis_api, web3_api)
