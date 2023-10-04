from propan.brokers.rabbit import RabbitExchange

from config_socketio.config_socketio import socket_rabbit_router
from src.core.register import RegisterContainer
from src.delivery.models import Order
from src.ibay.enums import OrderStatus
from src.ibay.services.ibay import IbayService

ibay_exchange = RabbitExchange(name='ibay_exchange')


@socket_rabbit_router.handle('check_orders_status', exchange=ibay_exchange)
async def check_orders_status(
        transaction_data
) -> None:
    ibay_service: IbayService = RegisterContainer.ibay_container.ibay_service()
    new_orders: list[Order] = await ibay_service.get_new_orders()
    refund_orders: list[Order] = await ibay_service.get_refund_orders()
    # TODO: refactor this
    for transaction in transaction_data:
        # find new order transactions
        for order in new_orders:
            if order.transaction.hash == transaction.get('hash'):
                status = transaction.get('status')
                await ibay_service.ordering(
                    order_id=order.id, status=OrderStatus.SUCCESS if status == 'SUCCESS' else OrderStatus.FAILED,
                    customer_id=order.customer_id, )

        # find refund order transactions
        for order in refund_orders:
            if order.return_transaction:
                if order.return_transaction.hash == transaction.get('hash'):
                    status = transaction.get('status')
                    await ibay_service.ordering(
                        order_id=order.id,
                        status=OrderStatus.REFUND if status == 'SUCCESS' else 'FAILED',
                        customer_id=order.customer_id,
                    )
