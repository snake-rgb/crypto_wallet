import passlib.hash
from dependency_injector import containers, providers
from src.core.containers import CoreContainer

from src.users.services.repository import UserRepository
from src.users.services.user import UserService


class UserContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=[
        'src.users', 'src.core', 'src.users.endpoints', 'config'
    ])
    password_hasher = providers.Callable(passlib.hash.pbkdf2_sha256.hash)
    user_repository = providers.Factory(UserRepository, CoreContainer.session)
    user_service = providers.Factory(UserService, user_repository, CoreContainer.session, password_hasher.provider)
