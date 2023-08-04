from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from src.users.containers import UserContainer
from src.users.schemas import UserForm
from src.users.services.repository import UserRepository
from src.users.services.user import UserService

register_router = APIRouter()


@register_router.get('/get_users/')
@inject
def get_users(
        user_service: UserService = Depends(Provide(UserContainer.user_service))
):
    return {'response': user_service.get_users()}


@register_router.get('/get_user_by_id/{user_id}')
@inject
def get_user_by_id(
        user_id: int,
        repository_service: UserRepository = Depends(Provide(UserContainer.user_repository))
):
    user = repository_service.get_by_id(user_id)
    return {'response': user}


@register_router.delete('/delete_user_by_id/{user_id}')
@inject
def delete_user_by_id(
        user_id: int,
        repository_service: UserRepository = Depends(Provide(UserContainer.user_repository))
):
    repository_service.delete_by_id(user_id)
    return {'response': 'success'}


@register_router.post('/create_user/')
@inject
def create_user(
        user_form: UserForm,
        user_service: UserService = Depends(Provide(UserContainer.user_service))
):
    user = user_service.create_user(user_form)
    return {'response': user}
