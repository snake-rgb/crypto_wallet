from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from src.auth.endpoints.auth import user_auth
from src.auth.services.auth import AuthService
from src.users.containers import UserContainer
from src.users.schemas import UserForm, ProfileSchema
from src.users.repositories.repository import UserRepository
from src.users.services.user import UserService

register_router = APIRouter()


@register_router.get('/get_users/')
@inject
async def get_users(
        user_service: UserService = Depends(Provide(UserContainer.user_service)),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth)
):
    users = await user_service.get_users()
    return {'response': users}


@register_router.get('/get_user_by_id/{user_id}')
@inject
async def get_user_by_id(
        user_id: int,
        user_service: UserService = Depends(Provide(UserContainer.user_service)),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth)
):
    user = await user_service.get_user_by_id(user_id)
    return {'response': user}


@register_router.delete('/delete_user_by_id/{user_id}')
@inject
async def delete_user_by_id(
        user_id: int,
        user_service: UserService = Depends(Provide(UserContainer.user_service)),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth)
):
    await user_service.delete_user_by_id(user_id)
    return {'response': 'success'}


@register_router.post('/register/')
@inject
async def register(
        user_form: UserForm,
        user_service: UserService = Depends(Provide(UserContainer.user_service)),
):
    user = await user_service.register(user_form)
    return {'response': user}


@register_router.get('/profile/')
@inject
async def profile(
        user_service: UserService = Depends(Provide(UserContainer.user_service)),
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
        user_service: UserService = Depends(Provide(UserContainer.user_service)),
        bearer: HTTPAuthorizationCredentials = Depends(user_auth),
):
    return {'response': await user_service.profile_edit(bearer.credentials, profile_schema=profile_schema)}
