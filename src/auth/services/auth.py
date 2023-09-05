from datetime import datetime, timedelta
from src.auth.dependencies.jwt_auth import create_access_token
from src.auth.schemas import LoginScheme
from src.auth.repositories.repository import AuthRepository
from src.users.models import User
from fastapi import Response


class AuthService:

    def __init__(self, auth_repository: AuthRepository) -> None:
        self.auth_repository = auth_repository

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
