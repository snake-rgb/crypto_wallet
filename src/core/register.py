from dependency_injector import providers, containers
from src.auth.containers import AuthContainer
from src.core.containers import CoreContainer
from src.users.containers import UserContainer
from src.wallet.containers import WalletContainer


class RegisterContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=[
        'src.users', 'src.auth', 'src.wallet', 'src.celery', 'src.core', 'config',
    ]
    )
    core_container = providers.Container(CoreContainer)
    users_container = providers.Container(UserContainer)
    wallet_container = providers.Container(WalletContainer)
    auth_container = providers.Container(AuthContainer)
