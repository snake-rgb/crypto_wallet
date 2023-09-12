from datetime import datetime, timedelta
from typing import Callable

from src.auth.dependencies.jwt_auth import create_access_token
from src.auth.schemas import LoginScheme, RegisterSchema
from src.auth.repositories.repository import AuthRepository
from src.users.models import User
from fastapi import Response
from src.auth.schemas import RegisterSchema
from fastapi import HTTPException


class AuthService:

    def __init__(self, auth_repository: AuthRepository, password_hasher: Callable[[str], str]) -> None:
        self.auth_repository = auth_repository
        self.password_hasher = password_hasher

    async def login(self, login_scheme: LoginScheme, response: Response) -> User:
        user = await self.auth_repository.login(login_scheme)
        if user:
            access_token = create_access_token(user.id, remember_me=login_scheme.remember_me)
            expire_time = datetime.utcnow() + timedelta(seconds=15)
            if login_scheme.remember_me:
                response.set_cookie(key="access_token", value=access_token, max_age=1707109200)

            else:
                response.set_cookie(key="access_token", value=access_token,
                                    expires=expire_time.strftime('%a, %d-%b-%Y %T GMT'))
            return user
        else:
            return {'response': 'Auth failed'}

    @staticmethod
    async def logout(response: Response) -> None:
        response.delete_cookie('access_token')

    async def register(self, register_schema: RegisterSchema, response: Response) -> User:
        hashed_password = self.password_hasher(register_schema.password)
        try:
            user = await self.auth_repository.register(register_schema, hashed_password=hashed_password)
            await self.login(login_scheme=LoginScheme(
                email=register_schema.email,
                password=register_schema.password,
                remember_me=True,
            ), response=response)
            return user
        except Exception:
            raise HTTPException(status_code=404, detail='Не удалось создать пользователя')
