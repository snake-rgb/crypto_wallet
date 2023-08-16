import passlib.hash
from dependency_injector import containers, providers
from src.users.repositories.repository import UserRepository
from src.users.services.user import UserService


class UserContainer(containers.DeclarativeContainer):
    # DB session
    session = providers.Dependency()
    boto3_service = providers.Dependency()
    # utils
    password_hasher = providers.Callable(passlib.hash.pbkdf2_sha256.hash)

    # repositories
    user_repository = providers.Singleton(UserRepository, session)
    # service
    user_service = providers.Singleton(UserService, user_repository, password_hasher.provider, boto3_service)
