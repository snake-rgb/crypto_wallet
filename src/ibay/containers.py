from dependency_injector import containers, providers

from src.ibay.repositories.repository import IbayRepository
from src.ibay.services.ibay import IbayService


class IbayContainer(containers.DeclarativeContainer):
    session = providers.Dependency()
    boto3_service = providers.Dependency()
    wallet_service = providers.Dependency()
    ibay_repository = providers.Singleton(IbayRepository, session)
    ibay_service = providers.Factory(IbayService, ibay_repository, boto3_service, wallet_service)
