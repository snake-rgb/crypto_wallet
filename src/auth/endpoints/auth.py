from datetime import datetime, timedelta
from src.users.tasks import send_register_email, user_chat_activate
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Response, Depends
from fastapi.security import HTTPAuthorizationCredentials
from src.auth.dependencies.jwt_auth import UserAuth
from src.auth.schemas import LoginScheme, RegisterSchema
from src.auth.services.auth import AuthService
from src.boto3.services.boto3 import Boto3Service
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
) -> dict:
    await auth_service.logout(response)
    return {'response': 'success'}


@auth_router.post('/register/')
@inject
async def register(
        register_schema: RegisterSchema,
        response: Response,
        auth_service: AuthService = Depends(Provide[RegisterContainer.auth_container.auth_service]),
) -> dict:
    register_schema.profile_image = None
    user = await auth_service.register(register_schema, response)
    if user:
        # user activation timer
        eta_time = datetime.utcnow() + timedelta(seconds=60)
        send_register_email.apply_async(args=[user.email, user.username])
        user_chat_activate.apply_async(args=[user.id], eta=eta_time)
        return {'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'profile_image': user.profile_image,
            'has_chat_access': user.has_chat_access,
            'is_active': user.is_active,
            'password': user.password,
        }}


@auth_router.get('/token_verify/')
@inject
async def token_verify(
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),
):
    return True
