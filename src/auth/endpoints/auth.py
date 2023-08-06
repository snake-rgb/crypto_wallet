from typing import Annotated
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, Response, Request
from fastapi.security import HTTPAuthorizationCredentials

from config import settings
from src.auth.containers import AuthContainer
from src.auth.dependencies.jwt_auth import UserAuth
from src.auth.schemas import LoginScheme
from src.auth.services.auth import AuthService
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

auth_router = APIRouter()

# Login check
user_auth = UserAuth()


@auth_router.post(
    '/login/',
    name='auth:login',
    summary='User login',
    description='Add user access token to cookies',
)
@inject
async def login(
        login_scheme: LoginScheme,
        response: Response,
        auth_service: AuthService = Depends(Provide(AuthContainer.auth_service))
):
    user = await auth_service.login(login_scheme, response)
    return {'response': user}


@auth_router.get(
    '/logout/',
    name='auth:logout',
    summary='User logout',
    description='Delete user access token from cookies',
    # response_model=HTTPAuthorizationCredentials
)
@inject
async def logout(
        response: Response,
        auth_service: AuthService = Depends(Provide(AuthContainer.auth_service)),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),
):
    await auth_service.logout(response)
    return {'response': 'success'}


@auth_router.get('/test/')
@inject
async def test(
        request: Request,
        auth_service: AuthService = Depends(Provide(AuthContainer.auth_service)),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),
):
    print(bearer)
    return {'response': 'success'}



