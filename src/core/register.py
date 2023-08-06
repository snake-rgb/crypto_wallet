from dependency_injector import providers, containers
from src.auth.containers import AuthContainer
from src.core.containers import CoreContainer
from src.users.containers import UserContainer


class RegisterContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=[
        'src.users', 'src.auth', 'src.core', 'src.users.endpoints', 'config', 'src.auth.dependencies'
    ]
    )
    users_container = providers.Container(UserContainer)
    auth_container = providers.Container(AuthContainer)
    core_container = providers.Container(CoreContainer)
