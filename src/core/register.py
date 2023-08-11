from dependency_injector import providers, containers
from src.auth.containers import AuthContainer
from src.core.containers import CoreContainer
from src.users.containers import UserContainer
from src.wallet.containers import WalletContainer


class RegisterContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=[
        # 'src.users', 'src.auth', 'src.wallet', 'src.core', 'config',
        'src', 'config'
    ]
    )
    core_container = providers.Container(CoreContainer)
    user_container = providers.Container(UserContainer,
                                         session=core_container.session)
    auth_container = providers.Container(AuthContainer,
                                         session=core_container.session,
                                         user_service=user_container.user_service)
    wallet_container = providers.Container(WalletContainer,
                                           session=core_container.session,
                                           user_service=user_container.user_service)
