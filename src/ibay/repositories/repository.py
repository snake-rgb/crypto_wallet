from typing import Callable, Iterator
from fastapi import HTTPException
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from src.delivery.models import Order
from src.ibay.enums import OrderStatus
from src.ibay.models import Product
from src.ibay.schemas import ProductSchema
from src.wallet.models import Transaction


class IbayRepository:
    def __init__(self, session_factory: Callable[..., AsyncSession]) -> None:
        self.session_factory = session_factory

    async def create_product(self, product_schema: ProductSchema) -> Product:
        async with self.session_factory() as session:
            product = Product(
                name=product_schema.name,
                image=product_schema.image,
                price=product_schema.price,
                wallet_address=product_schema.wallet_address,
            )
            session.add(product)
            await session.commit()
            await session.refresh(product)
            return product

    async def get_products(self) -> Iterator[Product]:
        async with self.session_factory() as session:
            query = await session.execute(select(Product))
            products = query.scalars().all()
            return products

    async def get_product_by_id(self, product_id: int) -> Product:
        async with self.session_factory() as session:
            query = await session.execute(select(Product).where(Product.id == product_id))
            product = query.scalar_one_or_none()
            if product:
                return product
            else:
                raise HTTPException(status_code=400, detail=f'Cant find product with id {product_id}')

    async def create_order(self, product_id: int, transaction_id: int, customer_id: int) -> dict:
        async with self.session_factory() as session:
            order: Order = Order(
                transaction_id=transaction_id,
                product_id=product_id,
                status=OrderStatus.NEW,
                customer_id=customer_id,
            )
            session.add(order)
            await session.commit()
            await session.refresh(order)
            query = await session.execute(select(Transaction).where(Transaction.id == order.transaction_id))
            transaction = query.scalar_one_or_none()
            query = await session.execute(select(Product).where(Product.id == order.product_id))
            product = query.scalar_one_or_none()

            return {
                'order': order,
                'transaction': transaction,
                'product': product,
            }

    async def get_new_orders(self) -> list[Order]:
        async with self.session_factory() as session:
            query = await session.execute(
                select(Order).options(joinedload(Order.transaction)).where(
                    Order.status == OrderStatus.NEW))
            orders = query.scalars().all()
            return orders

    async def get_refund_orders(self) -> list[Order]:
        async with self.session_factory() as session:
            query = await session.execute(
                select(Order).options(joinedload(Order.return_transaction)).where(
                    Order.status == OrderStatus.DELIVERY and Order.return_transaction_id.is_not(None)))
            orders = query.scalars().all()
            return orders

    async def set_order_status(self, order_id: int, status: str) -> Order:
        async with self.session_factory() as session:
            query = await session.execute(
                select(Order).options(joinedload(Order.transaction)).where(Order.id == order_id))
            order: Order = query.scalar_one_or_none()
            order.status = status
            session.add(order)
            await session.commit()
            await session.refresh(order)

    async def get_order_by_id(self, order_id: int) -> Order:
        async with self.session_factory() as session:
            query = await session.execute(
                select(Order).options(
                    joinedload(Order.transaction),
                    joinedload(Order.product),
                    joinedload(Order.return_transaction)).where(
                    Order.id == order_id))
            order = query.scalar_one_or_none()
            if order:
                return order
            else:
                raise HTTPException(status_code=400, detail=f'Cant find order with id {order_id}')

    async def update_order(self, order_id: int, return_transaction_id: int, status: str) -> Order:
        async with self.session_factory() as session:
            query = await session.execute(
                select(Order).options(joinedload(Order.transaction), joinedload(Order.return_transaction)).where(
                    Order.id == order_id))
            order: Order = query.scalar_one_or_none()
            if order:
                order.status = status
                order.return_transaction_id = return_transaction_id
                session.add(order)
                await session.commit()
                await session.refresh(order)
                return order
            else:
                raise HTTPException(status_code=404, detail='Cant find order with this id')

    async def get_user_orders(self, user_id: int) -> list[Order]:
        async with self.session_factory() as session:
            query = await session.execute(
                select(Order).options(joinedload(Order.product), joinedload(Order.transaction),
                                      joinedload(Order.return_transaction)).where(
                    Order.customer_id == user_id))
            orders = query.scalars().all()
            return orders

    async def get_latest_delivery_order(self) -> Order:
        async with self.session_factory() as session:
            query = await session.execute(
                select(Order).options().limit(1).where(
                    Order.status == OrderStatus.DELIVERY,
                    Order.return_transaction_id.is_(None)).order_by(Order.date))
            order = query.scalar_one_or_none()
            return order
