from dependency_injector import containers, providers
from src.auth.repositories.repository import AuthRepository
from src.auth.services.auth import AuthService
import passlib.hash


class AuthContainer(containers.DeclarativeContainer):
    session = providers.Dependency()

    # repository
    auth_repository = providers.Factory(AuthRepository, session)
    # utils
    password_hasher = providers.Callable(passlib.hash.pbkdf2_sha256.hash)
    # services
    auth_service = providers.Factory(AuthService, auth_repository, password_hasher.provider)
