from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from src.auth.endpoints.auth import user_auth
from src.core.register import RegisterContainer
from src.ibay.schemas import ProductSchema, OrderSchema
from src.ibay.services.ibay import IbayService

ibay_router = APIRouter(tags=['/ibay'])


@ibay_router.post('/create-product/')
@inject
async def create_product(
        product_schema: ProductSchema,
        ibay_service: IbayService = Depends(Provide[RegisterContainer.ibay_container.ibay_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth)
):
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


@ibay_router.post('/create-order/')
@inject
async def create_order(
        order_schema: OrderSchema,
        ibay_service: IbayService = Depends(Provide[RegisterContainer.ibay_container.ibay_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),

):
    response = await ibay_service.create_order(order_schema)
    return response
