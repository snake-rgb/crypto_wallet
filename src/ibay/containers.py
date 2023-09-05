from dependency_injector import containers, providers

from src.ibay.repositories.repository import IbayRepository
from src.ibay.services.ibay import IbayService


class IbayContainer(containers.DeclarativeContainer):
    session = providers.Dependency()
    ibay_repository = providers.Singleton(IbayRepository, session)
    ibay_service = providers.Factory(IbayService, ibay_repository)
