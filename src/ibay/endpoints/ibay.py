from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from src.auth.endpoints.auth import user_auth
from src.boto3.services.boto3 import Boto3Service
from src.core.register import RegisterContainer
from src.ibay.schemas import ProductSchema, OrderSchema
from src.ibay.services.ibay import IbayService

ibay_router = APIRouter(tags=['/ibay'])


@ibay_router.post('/create-product/')
@inject
async def create_product(
        product_schema: ProductSchema,
        ibay_service: IbayService = Depends(Provide[RegisterContainer.ibay_container.ibay_service]),
        boto3_service: Boto3Service = Depends(Provide[RegisterContainer.boto3_container.boto3_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth)
):
    image = await boto3_service.upload_image(product_schema.image)
    product_schema.image = image
    response = await ibay_service.create_product(product_schema)
    return response


@ibay_router.get('/products/')
@inject
async def get_products(
        ibay_service: IbayService = Depends(Provide[RegisterContainer.ibay_container.ibay_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth)
):
    response = await ibay_service.get_products()
    return response


@ibay_router.get('/get-product-by-id/')
@inject
async def get_product_by_id(
        product_id: int,
        ibay_service: IbayService = Depends(Provide[RegisterContainer.ibay_container.ibay_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),

):
    response = await ibay_service.get_product_by_id(product_id)
    return response


@ibay_router.post('/buy-product/')
@inject
async def buy_product(
        order_schema: OrderSchema,
        ibay_service: IbayService = Depends(Provide[RegisterContainer.ibay_container.ibay_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),

):
    response = await ibay_service.buy_product(order_schema, bearer)
    return response


@ibay_router.get('/user-orders/')
@inject
async def get_user_orders(
        ibay_service: IbayService = Depends(Provide[RegisterContainer.ibay_container.ibay_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),

):
    response = await ibay_service.get_user_orders(bearer)
    return response


@ibay_router.get('/latest-order/')
@inject
async def get_user_orders(
        ibay_service: IbayService = Depends(Provide[RegisterContainer.ibay_container.ibay_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),

):
    response = await ibay_service.get_latest_delivery_order()
    return response
