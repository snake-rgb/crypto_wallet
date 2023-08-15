from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Response, Request, Depends
from fastapi.security import HTTPAuthorizationCredentials
from src.auth.dependencies.jwt_auth import UserAuth
from src.auth.schemas import LoginScheme
from src.auth.services.auth import AuthService
from src.core.register import RegisterContainer

auth_router = APIRouter(tags=['auth'])

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
        auth_service: AuthService = Depends(Provide[RegisterContainer.auth_container.auth_service])
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
        auth_service: AuthService = Depends(Provide[RegisterContainer.auth_container.auth_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),
):
    await auth_service.logout(response)
    return {'response': 'success'}
