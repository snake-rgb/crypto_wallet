from typing import Callable, Iterator, Optional
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.ibay.models import Product, Order
from src.ibay.schemas import ProductSchema, OrderSchema


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

    async def create_order(self, order_schema: OrderSchema) -> Order:
        async with self.session_factory() as session:
            order = Order(
                transaction_id=order_schema.transaction_id,
                return_transaction_id=order_schema.return_transaction_id if order_schema.return_transaction_id else None,
                product_id=order_schema.product_id,
                status=order_schema.status,
            )
            # session.add(order)
            # await session.commit()
            # await session.refresh(order)
            return order
