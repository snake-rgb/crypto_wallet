from dependency_injector import containers, providers
from src.wallet.repositories.repository import WalletRepository
from src.wallet.service.wallet import WalletService


class WalletContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=[
        'src.users', 'src.auth', 'src.wallet', 'src.core', 'config',
    ]
    )
    session = providers.Dependency()
    user_service = providers.Dependency()
    # repository
    wallet_repository = providers.Factory(WalletRepository, session)

    # services
    wallet_service = providers.Factory(WalletService, wallet_repository, user_service)
