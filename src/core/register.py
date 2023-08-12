from dependency_injector import providers, containers
from src.core.containers import CoreContainer
from src.users.containers import UserContainer
from src.wallet.containers import WalletContainer
from src.api.containers import APIContainer
from src.auth.containers import AuthContainer


class RegisterContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=[
        # 'src.users', 'src.auth', 'src.wallet', 'src.core', 'config',
        'src', 'config'
    ]
    )
    api_container = providers.Container(APIContainer)
    core_container = providers.Container(CoreContainer)
    user_container = providers.Container(UserContainer,
                                         session=core_container.session)
    auth_container = providers.Container(AuthContainer,
                                         session=core_container.session,
                                         user_service=user_container.user_service)
    wallet_container = providers.Container(WalletContainer,
                                           session=core_container.session,
                                           user_service=user_container.user_service,
                                           moralis_api=api_container.moralis_api)
