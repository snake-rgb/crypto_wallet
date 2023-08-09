from dependency_injector import containers, providers
from src.auth.repositories.repository import AuthRepository
from src.auth.services.auth import AuthService
from src.core.containers import CoreContainer
from src.users.containers import UserContainer


class AuthContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=[
        'src.users', 'src.auth', 'src.celery', 'src.wallet', 'src.core', 'config',
    ]
    )
    # repository
    auth_repository = providers.Factory(AuthRepository, CoreContainer.session)

    # services
    auth_service = providers.Factory(AuthService, auth_repository, UserContainer.user_service)
