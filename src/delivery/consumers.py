from propan.brokers.rabbit import RabbitExchange

from config_fastapi.config_fastapi import rabbit_router
from src.core.register import RegisterContainer
from src.delivery.services.delivery import DeliveryService

delivery_exchange = RabbitExchange(name='delivery_exchange')


@rabbit_router.handle('run_delivery', exchange=delivery_exchange)
async def run_delivery(
        data
) -> None:
    delivery_service: DeliveryService = RegisterContainer.delivery_container.delivery_service()
    return await delivery_service.run_delivery()
