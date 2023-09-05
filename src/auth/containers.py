from dependency_injector import containers, providers
from src.auth.repositories.repository import AuthRepository
from src.auth.services.auth import AuthService


class AuthContainer(containers.DeclarativeContainer):
    session = providers.Dependency()

    # repository
    auth_repository = providers.Factory(AuthRepository, session)

    # services
    auth_service = providers.Factory(AuthService, auth_repository)
