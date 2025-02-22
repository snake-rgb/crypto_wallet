from dependency_injector import containers, providers
from src.wallet.repositories.repository import WalletRepository
from src.wallet.service.wallet import WalletService


class WalletContainer(containers.DeclarativeContainer):
    session = providers.Dependency()
    # repository
    wallet_repository = providers.Factory(WalletRepository, session)

    # services
    wallet_service = providers.Factory(WalletService, wallet_repository)
