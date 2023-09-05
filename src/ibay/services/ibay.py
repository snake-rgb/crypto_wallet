import decimal
import random
from typing import Iterator
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from propan import RabbitBroker
from config import settings
from src.auth.dependencies import jwt_auth
from src.delivery.google_request import run_delivery
from src.ibay.enums import OrderStatus
from src.ibay.models import Product, Order
from src.ibay.repositories.repository import IbayRepository
from src.ibay.schemas import ProductSchema, OrderSchema


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
            await broker.publish({
                'from_address': order_schema.from_address,
                'to_address': product.wallet_address,
                'amount': product.price,
                'customer_id': customer_id,
                'product_id': product.id,
            },
                queue='send_transaction')
        return product

    async def create_order(self, product_id: int, transaction_id: int, customer_id: int) -> Order:
        return await self.ibay_repository.create_order(product_id, transaction_id, customer_id)

    async def get_new_orders(self) -> list[Order]:
        return await self.ibay_repository.get_new_orders()

    async def get_refund_orders(self) -> list[Order]:
        return await self.ibay_repository.get_refund_orders()

    async def ordering(self, order_id: int, status: str) -> None:
        if status == OrderStatus.SUCCESS:
            delivery_status: bool = await run_delivery()
            await self.delivery_status(order_id, delivery_status)
        elif status == OrderStatus.REFUND:
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

        async with RabbitBroker(settings.RABBITMQ_URL) as broker:
            await broker.publish({
                'from_address': from_address,
                'to_address': to_address,
                'amount': order.product.price * decimal.Decimal(1.5),
                'customer_id': order.customer_id,
                'product_id': order.product.id,
                'order_id': order.id
            },
                queue='order_refund', exchange='wallet_exchange')

    async def get_user_orders(self, bearer: HTTPAuthorizationCredentials) -> list[Order]:
        user_id = jwt_auth.decode_token(bearer.credentials).get('user_id')
        return await self.ibay_repository.get_user_orders(user_id)

    async def get_latest_delivery_order(self) -> Order:
        return await self.ibay_repository.get_latest_delivery_order()

    async def delivery(self) -> bool:
        order = await self.get_latest_delivery_order()
        if order:
            delivery_chance: bool = bool(random.randrange(2))
            if delivery_chance:
                await self.ibay_repository.set_order_status(order.id, OrderStatus.SUCCESS)
            else:
                await self.order_refund(order.id)
                await self.ibay_repository.set_order_status(order.id, OrderStatus.DELIVERY)
            print('Delivery - ', delivery_chance)
        else:
            print('Cant find orders with status delivery')

    async def update_order(self, order_id: int, return_transaction_id: int, status: OrderStatus) -> Order:
        return await self.ibay_repository.update_order(order_id, return_transaction_id, status)
