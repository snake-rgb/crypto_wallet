import logging

from celery import Celery
from dependency_injector import providers, containers

from config import settings
from config_celery import celery_config
from src.core.containers import CoreContainer
from src.parser.containers import ParserContainer
from src.users.containers import UserContainer
from src.wallet.containers import WalletContainer
from src.api.containers import APIContainer
from src.auth.containers import AuthContainer
from src.boto3.containers import Boto3Container


class RegisterContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            'config',
            'config_fastapi',
            'config_socketio',
            # 'config_celery',
            'src.core',
            'src.api',
            'src.auth',
            'src.base',
            'src.boto3',
            'src.ibay',
            'src.parser',
            'src.users',
            'src.wallet',
        ],
    )

    celery = providers.Singleton(
        Celery,
        broker=settings.RABBITMQ_URL,
        include=['src.users.tasks', ],
        backend=settings.CELERY_RESULT_BACKEND
    )
    api_container = providers.Container(APIContainer)
    core_container = providers.Container(CoreContainer)
    boto3_container = providers.Container(Boto3Container, session=core_container.session)
    user_container = providers.Container(
        UserContainer,
        session=core_container.session,
        boto3_service=boto3_container.boto3_service
    )

    auth_container = providers.Container(
        AuthContainer,
        session=core_container.session,
        user_service=user_container.user_service)

    wallet_container = providers.Container(
        WalletContainer,
        session=core_container.session,
        user_service=user_container.user_service,
        moralis_api=api_container.moralis_api,
        web3_api=api_container.web3_api,
        boto3_service=boto3_container.boto3_service)

    parser_container = providers.Container(
        ParserContainer,
        web3_api=api_container.web3_api,
        wallet_service=wallet_container.wallet_service
    )
