from propan.brokers.rabbit import RabbitExchange

from config_socketio.config_socketio import socket_rabbit_router
from src.core.register import RegisterContainer
from src.ibay.enums import OrderStatus
from src.ibay.models import Order
from src.ibay.schemas import ProductSchema
from src.ibay.services.ibay import IbayService
from src.wallet.models import Transaction
from src.wallet.service.wallet import WalletService

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

# @socket_rabbit_router.handle('create_order', exchange=ibay_exchange)
# async def create_order(
#         data
# ) -> Order:
#     ibay_service: IbayService = RegisterContainer.ibay_container.ibay_service()
#     order = await ibay_service.create_order(
#         product_id=data.get('product_id'),
#         transaction_id=data.get('transaction_id'),
#         customer_id=data.get('customer_id'),
#     )
#
#     return order


# @socket_rabbit_router.handle('order_refund', exchange=ibay_exchange)
# async def order_refund(
#         data
# ) -> None:
#     ibay_service: IbayService = RegisterContainer.ibay_container.ibay_service()
#     await ibay_service.update_order(
#         order_id=data.get('order_id'),
#         return_transaction_id=data.get('return_transaction_id'),
#         status=OrderStatus.DELIVERY,
#     )
