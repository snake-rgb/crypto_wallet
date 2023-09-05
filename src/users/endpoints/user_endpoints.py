from datetime import datetime, timedelta

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from src.auth.endpoints.auth import user_auth
from src.boto3.services.boto3 import Boto3Service
from src.core.register import RegisterContainer
from src.users.schemas import UserForm, ProfileSchema
from src.users.services.user import UserService
from src.users.tasks import send_register_email, user_chat_activate

register_router = APIRouter(tags=['user'])


@register_router.get('/get_users/')
@inject
async def get_users(
        user_service: UserService = Depends(Provide[RegisterContainer.user_container.user_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth)
):
    users = await user_service.get_users()
    return {'response': users}


@register_router.get('/get_user_by_id/{user_id}')
@inject
async def get_user_by_id(
        user_id: int,
        user_service: UserService = Depends(Provide[RegisterContainer.user_container.user_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth)
):
    user = await user_service.get_user_by_id(user_id)
    return {'response': user}


@register_router.delete('/delete_user_by_id/{user_id}')
@inject
async def delete_user_by_id(
        user_id: int,
        user_service: UserService = Depends(Provide[RegisterContainer.user_container.user_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth)
):
    await user_service.delete_user_by_id(user_id)
    return {'response': 'success'}


@register_router.post('/register/')
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
        eta_time = datetime.utcnow() + timedelta(seconds=5)
        send_register_email.apply_async(args=[user.email, user.username])
        user_chat_activate.apply_async(args=[user.id], eta=eta_time)
    return {'response': user}


@register_router.get('/profile/')
@inject
async def profile(
        user_service: UserService = Depends(Provide[RegisterContainer.user_container.user_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),
):
    return {'response': await user_service.profile(bearer.credentials)}


@register_router.put(
    '/profile/edit',
    description='Profile edit',
    summary='Profile edit',
)
@inject
async def profile_edit(
        profile_schema: ProfileSchema,
        user_service: UserService = Depends(Provide[RegisterContainer.user_container.user_service]),
        boto3_service: Boto3Service = Depends(Provide[RegisterContainer.boto3_container.boto3_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),
):
    if profile_schema.profile_image != '':
        profile_schema.profile_image = await boto3_service.upload_image(profile_schema.profile_image)
    return {'response': await user_service.profile_edit(bearer.credentials, profile_schema=profile_schema)}
