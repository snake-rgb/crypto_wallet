from dependency_injector import containers, providers

from src.core.containers import CoreContainer
from src.wallet.repositories.repository import WalletRepository
from src.wallet.service.wallet import WalletService


class WalletContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=[
        'src.core', 'src.wallet', 'src.users', 'src.auth', 'src.celery', 'config',
    ]
    )
    # repository
    wallet_repository = providers.Factory(WalletRepository, CoreContainer.session)

    # services
    wallet_service = providers.Factory(WalletService, wallet_repository)
