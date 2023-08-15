from dependency_injector import providers, containers
from src.core.containers import CoreContainer
from src.parser.containers import ParserContainer
from src.users.containers import UserContainer
from src.wallet.containers import WalletContainer
from src.api.containers import APIContainer
from src.auth.containers import AuthContainer


class RegisterContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=['src', 'config', 'config_fastapi', 'config_socketio', 'config_celery']
    )

    api_container = providers.Container(APIContainer)
    core_container = providers.Container(CoreContainer)

    user_container = providers.Container(
        UserContainer,
        session=core_container.session)

    auth_container = providers.Container(
        AuthContainer,
        session=core_container.session,
        user_service=user_container.user_service)

    wallet_container = providers.Container(
        WalletContainer,
        session=core_container.session,
        user_service=user_container.user_service,
        moralis_api=api_container.moralis_api,
        web3_api=api_container.web3_api)

    parser_container = providers.Container(
        ParserContainer,
        web3_api=api_container.web3_api,
    )
