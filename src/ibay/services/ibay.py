import decimal
import random
from typing import Iterator
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from propan import RabbitBroker
from config import settings
from src.auth.dependencies import jwt_auth
from src.delivery.models import Order
from src.ibay.enums import OrderStatus
from src.ibay.models import Product
from src.ibay.repositories.repository import IbayRepository
from src.ibay.schemas import ProductSchema, OrderSchema
from src.wallet.models import Transaction


class IbayService:
    def __init__(self,
                 ibay_repository: IbayRepository,
                 ):
        self.ibay_repository = ibay_repository

    async def create_product(self, product_schema: ProductSchema) -> Product:
        return await self.ibay_repository.create_product(product_schema)

    async def get_products(self) -> Iterator[Product]:
        return await self.ibay_repository.get_products()

    async def get_product_by_id(self, product_id: int) -> Product:
        return await self.ibay_repository.get_product_by_id(product_id)

    async def buy_product(self, order_schema: OrderSchema, bearer: HTTPAuthorizationCredentials) -> Product:
        customer_id = jwt_auth.decode_token(bearer.credentials).get('user_id')
        product = await self.get_product_by_id(order_schema.product_id)

        async with RabbitBroker(settings.RABBITMQ_URL) as broker:
            transaction_id: int = await broker.publish({
                'from_address': order_schema.from_address,
                'to_address': product.wallet_address,
                'amount': product.price,
                'customer_id': customer_id,
                'product_id': product.id,
            },
                queue='send_transaction', exchange='wallet_exchange', callback=True)
        await self.create_order(product_id=product.id, transaction_id=transaction_id,
                                customer_id=customer_id)
        return product

    async def create_order(self, product_id: int, transaction_id: int, customer_id: int) -> Order:
        result: dict = await self.ibay_repository.create_order(product_id, transaction_id,
                                                               customer_id)
        order: Order = result.get('order')
        transaction: Transaction = result.get('transaction')
        product: Product = result.get('product')
        async with RabbitBroker(settings.RABBITMQ_URL) as broker:
            await broker.publish({
                'id': order.id,
                'title': product.name,
                'transaction_hash': transaction.hash,
                'price': product.price,
                'image': product.image,
                'status': order.status,
                'time': order.date,
                'user_id': order.customer_id,

            },
                queue='create_order',
                exchange='socketio_exchange')
        return order

    async def get_new_orders(self) -> list[Order]:
        return await self.ibay_repository.get_new_orders()

    async def get_refund_orders(self) -> list[Order]:
        return await self.ibay_repository.get_refund_orders()

    async def ordering(self, order_id: int, status: str, customer_id: int) -> None:
        if status == OrderStatus.SUCCESS:
            async with RabbitBroker(settings.RABBITMQ_URL) as broker:
                delivery_status: bool = await broker.publish({
                },
                    queue='run_delivery', exchange='delivery_exchange')
            await self.delivery_status(order_id, delivery_status)
            async with RabbitBroker(settings.RABBITMQ_URL) as broker:
                await broker.publish({
                    'order_id': order_id,
                    'status': OrderStatus.DELIVERY,
                    'user_id': customer_id,
                },
                    queue='order_status',
                    exchange='socketio_exchange')
        elif status == OrderStatus.REFUND:
            async with RabbitBroker(settings.RABBITMQ_URL) as broker:
                await broker.publish({
                    'order_id': order_id,
                    'status': OrderStatus.REFUND,
                    'user_id': customer_id,
                },
                    queue='order_status',
                    exchange='socketio_exchange')
            await self.ibay_repository.set_order_status(order_id, OrderStatus.REFUND)
        else:
            raise HTTPException(status_code=404, detail='Error order status')

    async def delivery_status(self, order_id: int, status: bool):
        if status:
            await self.ibay_repository.set_order_status(order_id, OrderStatus.DELIVERY)
        else:
            await self.ibay_repository.set_order_status(order_id, OrderStatus.FAILED)
            await self.order_refund(order_id)

    async def order_refund(self, order_id: int) -> None:
        order: Order = await self.ibay_repository.get_order_by_id(order_id)
        from_address: str = order.transaction.to_address
        to_address: str = order.transaction.from_address
        # TODO: Make commission
        fee = (order.transaction.fee * (decimal.Decimal(1.5)) / (10 ** 18))
        async with RabbitBroker(settings.RABBITMQ_URL) as broker:
            transaction_data: dict = await broker.publish({
                'from_address': from_address,
                'to_address': to_address,
                'amount': order.product.price - fee,
                'customer_id': order.customer_id,
                'product_id': order.product.id,
                'order_id': order.id
            },
                queue='order_refund', exchange='wallet_exchange', callback=True)
        if transaction_data:
            await self.update_order(
                order_id,
                return_transaction_id=transaction_data.get('return_transaction_id'),
                status=OrderStatus.DELIVERY,
            )

    async def get_user_orders(self, bearer: HTTPAuthorizationCredentials) -> list[Order]:
        user_id = jwt_auth.decode_token(bearer.credentials).get('user_id')
        return await self.ibay_repository.get_user_orders(user_id)

    async def get_latest_delivery_order(self) -> Order:
        return await self.ibay_repository.get_latest_delivery_order()

    async def delivery(self) -> bool:
        order = await self.get_latest_delivery_order()
        if order:
            delivery_chance: bool = bool(random.randrange(0, 2))
            if delivery_chance:
                async with RabbitBroker(settings.RABBITMQ_URL) as broker:
                    await broker.publish({
                        'order_id': order.id,
                        'status': OrderStatus.SUCCESS,
                        'user_id': order.customer_id,
                    },
                        queue='order_status',
                        exchange='socketio_exchange')
                await self.ibay_repository.set_order_status(order.id, OrderStatus.SUCCESS)
            else:
                await self.order_refund(order.id)
                await self.ibay_repository.set_order_status(order.id, OrderStatus.DELIVERY)
        else:
            print('Cant find orders with status delivery')

    async def update_order(self, order_id: int, return_transaction_id: int, status: OrderStatus) -> Order:
        order = await self.ibay_repository.update_order(order_id, return_transaction_id, status)
        if order:
            async with RabbitBroker(settings.RABBITMQ_URL) as broker:
                await broker.publish({
                    'order_id': order.id,
                    'status': status,
                    'user_id': order.customer_id,
                    'return_transaction_hash': order.return_transaction.hash if order.return_transaction else None
                },
                    queue='order_status',
                    exchange='socketio_exchange')
        return order
