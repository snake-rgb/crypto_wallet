from datetime import datetime, timedelta
from src.users.tasks import send_register_email, user_chat_activate
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Response, Depends
from fastapi.security import HTTPAuthorizationCredentials
from src.auth.dependencies.jwt_auth import UserAuth
from src.auth.schemas import LoginScheme
from src.auth.services.auth import AuthService
from src.boto3.services.boto3 import Boto3Service
from src.core.register import RegisterContainer
from src.users.schemas import UserForm
from src.users.services.user import UserService

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


@auth_router.post('/register/')
@inject
async def register(
        user_form: UserForm,
        user_service: UserService = Depends(Provide[RegisterContainer.user_container.user_service]),
        boto3_service: Boto3Service = Depends(Provide[RegisterContainer.boto3_container.boto3_service]),
):
    user_form.profile_image = await boto3_service.upload_image(user_form.profile_image)
    user = await user_service.register(user_form)
    if user:
        # user activation timer
        eta_time = datetime.utcnow() + timedelta(seconds=60)
        send_register_email.apply_async(args=[user.email, user.username])
        user_chat_activate.apply_async(args=[user.id], eta=eta_time)
    return {'response': user}
