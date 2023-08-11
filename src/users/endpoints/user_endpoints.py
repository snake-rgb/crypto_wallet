from propan.fastapi import RabbitRouter
from config import settings
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from src.auth.endpoints.auth import user_auth
from src.users.containers import UserContainer
from src.users.schemas import UserForm, ProfileSchema
from src.users.services.user import UserService

register_router = APIRouter(tags=['user'])
user_rabbit_router = RabbitRouter(settings.RABBITMQ_URL)


@user_rabbit_router.event('helloworld')
async def helloworld():
    print('hello world from broker')


@user_rabbit_router.get('/my_test/')
async def my_test():
    await user_rabbit_router.broker.publish("Hello, Rabbit!", "helloworld")


@register_router.get('/get_users/')
@inject
async def get_users(
        user_service: UserService = Depends(Provide[UserContainer.user_service]),
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
    # send_register_email.apply_async(args=[user.email, user.username])
    # user_chat_activate.apply_async(args=[user.id])
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
