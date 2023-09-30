from celery import Celery
from dependency_injector import providers, containers
from config import settings
from src.chat.containers import ChatContainer
from src.core.containers import CoreContainer
from src.delivery.containers import DeliveryContainer
from src.ibay.containers import IbayContainer
from src.parser.containers import ParserContainer
from src.users.containers import UserContainer
from src.wallet.containers import WalletContainer
from src.moralis.containers import MoralisContainer
from src.auth.containers import AuthContainer
from src.boto3.containers import Boto3Container
from src.web3.containers import Web3Container


class RegisterContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            'config',
            'config_fastapi',
            'config_socketio',
            'src.core',
            'src.auth',
            'src.base',
            'src.boto3',
            'src.ibay',
            'src.parser',
            'src.users',
            'src.wallet',
            'src.chat',
            'src.web3',
            'src.moralis',
            'src.delivery',
        ],
    )

    celery = providers.Singleton(
        Celery,
        broker=settings.RABBITMQ_URL,
        include=['src.users.tasks', ],
        backend=settings.CELERY_RESULT_BACKEND
    )
    moralis_container = providers.Container(MoralisContainer)
    web3_container = providers.Container(Web3Container)
    core_container = providers.Container(CoreContainer)
    boto3_container = providers.Container(
        Boto3Container,
        session=core_container.session)
    user_container = providers.Container(
        UserContainer,
        session=core_container.session,
    )

    auth_container = providers.Container(
        AuthContainer,
        session=core_container.session, )

    wallet_container = providers.Container(
        WalletContainer,
        session=core_container.session)

    parser_container = providers.Container(
        ParserContainer,
        celery=celery,
    )
    ibay_container = providers.Container(
        IbayContainer,
        session=core_container.session,
    )

    chat_container = providers.Container(
        ChatContainer,
        session=core_container.session,
    )

    delivery_container = providers.Container(DeliveryContainer)
