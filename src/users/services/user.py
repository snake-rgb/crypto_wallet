from typing import Callable
from src.auth.dependencies.jwt_auth import decode_token
from src.users.models import User
from src.users.schemas import ProfileSchema
from src.users.repositories.repository import UserRepository


class UserService:

    def __init__(
            self,
            user_repository: UserRepository,
            password_hasher: Callable[[str], str],

    ) -> None:
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    async def get_users(self):
        return await self.user_repository.get_all()

    async def get_user_by_id(self, user_id: int):
        return await self.user_repository.get_by_id(user_id)

    async def delete_user_by_id(self, user_id: int) -> None:
        return await self.user_repository.delete_by_id(user_id)

    async def profile(self, access_token: str) -> User:
        payload = decode_token(access_token)
        user = await self.user_repository.get_by_id(payload.get('user_id'))
        return user

    async def profile_edit(self, access_token: str, profile_schema: ProfileSchema) -> User:
        if profile_schema.password is not None:
            hashed_password = self.password_hasher(profile_schema.password)
            return await self.user_repository.profile_edit(access_token, profile_schema, hashed_password)
        else:
            return await self.user_repository.profile_edit(access_token, profile_schema, hashed_password=None)

    async def chat_activate(self, user_id: int) -> User:
        return await self.user_repository.chat_activate(user_id)




