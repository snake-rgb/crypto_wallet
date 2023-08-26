from typing import Iterator

from fastapi import HTTPException
from propan import RabbitBroker

from config import settings
from src.boto3.services.boto3 import Boto3Service
from src.ibay.models import Product, Order
from src.ibay.repositories.repository import IbayRepository
from src.ibay.schemas import ProductSchema, OrderSchema
from src.wallet.service.wallet import WalletService


class IbayService:
    def __init__(self,
                 ibay_repository: IbayRepository,
                 boto3_service: Boto3Service,
                 wallet_service: WalletService,
                 ):
        self.ibay_repository = ibay_repository
        self.boto3_service = boto3_service
        self.wallet_service = wallet_service

    async def create_product(self, product_schema: ProductSchema) -> Product:
        product_schema.image = await self.boto3_service.upload_image(product_schema.image)
        if product_schema.image:
            return await self.ibay_repository.create_product(product_schema)
        else:
            raise HTTPException(status_code=400, detail='Error')

    async def get_products(self) -> Iterator[Product]:
        return await self.ibay_repository.get_products()

    async def get_product_by_id(self, product_id: int) -> Product:
        return await self.ibay_repository.get_product_by_id(product_id)

    async def create_order(self, order_schema: OrderSchema) -> Order:
        order = await self.ibay_repository.create_order(order_schema)
        transaction = await self.wallet_service.get_transaction_by_id(transaction_id=order_schema.transaction_id)
        print(transaction.status)
        return order
