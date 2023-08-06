import passlib.hash
from dependency_injector import containers, providers
from src.core.containers import CoreContainer
from src.users.repositories.repository import UserRepository
from src.users.services.user import UserService


class UserContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=[
        'src.users', 'src.auth', 'src.core', 'src.users.endpoints', 'config', 'src.auth.dependencies'
    ], modules=['src.auth.containers']
    )

    password_hasher = providers.Callable(passlib.hash.pbkdf2_sha256.hash)
    # repositories
    user_repository = providers.Factory(UserRepository, CoreContainer.session)
    # service
    user_service = providers.Factory(UserService, user_repository, CoreContainer.session, password_hasher.provider)
