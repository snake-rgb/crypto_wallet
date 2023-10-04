from dependency_injector.wiring import inject, Provide
from sqladmin import action
from sqladmin.authentication import AuthenticationBackend
from fastapi import Depends, HTTPException
from starlette.requests import Request

from starlette.responses import Response, RedirectResponse

from src.auth.dependencies.jwt_auth import create_access_token, token_verify
from src.auth.schemas import LoginScheme
from src.auth.services.auth import AuthService
from src.core.register import RegisterContainer
from src.users.models import User
from src.users.services.user import UserService


class AdminAuth(AuthenticationBackend):

    @action(
        name="login",
        label="Login",
    )
    @inject
    async def login(self,
                    request: Request,
                    auth_service: AuthService = Depends(
                        Provide[RegisterContainer.auth_container.auth_service])) -> bool:

        form = request.query_params
        email, password = form.get('email'), form.get('password')

        user = await auth_service.login(LoginScheme(
            email=email,
            password=password,
            remember_me=True
        ), response=Response())
        if type(user) == User:
            if user.is_admin:
                access_token = create_access_token(user.id, remember_me=True)
                request.session.update({'access_token': access_token})
                return True
            else:
                raise HTTPException(status_code=403, detail='Недостаточно прав доступа')
        else:
            raise HTTPException(status_code=403, detail='Неверный логин или пароль')

    @inject
    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    @inject
    async def authenticate(self, request: Request,
                           user_service: UserService = Depends(
                               Provide[RegisterContainer.user_container.user_service])
                           ) -> bool:
        token = request.session.get("access_token")

        if token:
            token = token.replace('Bearer ', '')
            user = await user_service.profile(token)
            if user.is_admin:
                token_verify(token)
                return True
            else:
                request.session.clear()
                return RedirectResponse('/admin/login')
        else:
            request.session.clear()
            return RedirectResponse('/admin/login')
