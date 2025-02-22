from typing import Iterator

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from src.auth.endpoints.auth import user_auth
from src.boto3.services.boto3 import Boto3Service
from src.core.register import RegisterContainer
from src.users.models import User
from src.users.schemas import ProfileSchema
from src.users.services.user import UserService

register_router = APIRouter(tags=['user'])


@register_router.get('/get_users/')
@inject
async def get_users(
        user_service: UserService = Depends(Provide[RegisterContainer.user_container.user_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth)
) -> dict:
    users = await user_service.get_users()
    return {'users': [{
        'id': user.id,
        'username': user.username,
        'password': user.password,
        'profile_image': user.profile_image,
        'email': user.email,
        'is_active': user.is_active,
        'has_chat_access': user.has_chat_access,
    } for user in users]}


@register_router.get('/get_user_by_id/{user_id}')
@inject
async def get_user_by_id(
        user_id: int,
        user_service: UserService = Depends(Provide[RegisterContainer.user_container.user_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth)
) -> dict:
    user = await user_service.get_user_by_id(user_id)
    return {'user': {
        'id': user.id,
        'username': user.username,
        'password': user.password,
        'profile_image': user.profile_image,
        'email': user.email,
        'is_active': user.is_active,
        'has_chat_access': user.has_chat_access,
    }}


@register_router.get('/profile/')
@inject
async def profile(
        user_service: UserService = Depends(Provide[RegisterContainer.user_container.user_service]),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),
) -> dict:
    user = await user_service.profile(bearer.credentials)
    return {
        'id': user.id,
        'email': user.email,
        'username': user.username,
        'profile_image': user.profile_image,
        'has_chat_access': user.has_chat_access,
        'is_active': user.is_active,
        'password': user.password,
    }


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
) -> dict:
    if profile_schema.profile_image != '':
        profile_schema.profile_image = await boto3_service.upload_image(profile_schema.profile_image)
    user = await user_service.profile_edit(bearer.credentials, profile_schema=profile_schema)
    return {
        'username': user.username,
        'email': user.email,
        'profile_image': user.profile_image,
        'password': user.password,
        'id': user.id,

    }

# @register_router.get(
#     '/users/online',
# )
# @inject
# async def get_online_users(
#         user_service: UserService = Depends(Provide[RegisterContainer.user_container.user_service]),
#         bearer: HTTPAuthorizationCredentials = Depends(user_auth),
# ) -> dict:
#     users = await user_service.get_online_users()
#
#     return {'users': [
#         {
#             'id': user.id,
#             'username': user.username,
#             'profile_image': user.profile_image,
#             'is_online': user.is_online
#         }
#         for user in users]}
