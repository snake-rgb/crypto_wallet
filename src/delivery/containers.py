from dependency_injector import containers, providers

from src.delivery.services.delivery import DeliveryService


class DeliveryContainer(containers.DeclarativeContainer):
    delivery_service = providers.Factory(DeliveryService)
