from datetime import datetime, timedelta
from typing import Callable
from sqlalchemy.orm import Session
from src.auth.dependencies.jwt_auth import decode_token
from src.users.models import User
from src.users.schemas import UserForm, ProfileSchema
from src.users.repositories.repository import UserRepository



class UserService:

    def __init__(self, user_repository: UserRepository, session_factory: Callable[..., Session],
                 password_hasher: Callable[[str], str]) -> None:
        self.user_repository = user_repository
        self.session_factory = session_factory
        self.password_hasher = password_hasher

    async def get_users(self):
        return await self.user_repository.get_all()

    async def get_user_by_id(self, user_id: int):
        return await self.user_repository.get_by_id(user_id)

    async def delete_user_by_id(self, user_id: int) -> None:
        return await self.user_repository.delete_by_id(user_id)

    async def register(self, user_form: UserForm) -> User:
        hashed_password = self.password_hasher(user_form.password)
        user = await self.user_repository.register(user_form, hashed_password=hashed_password)
        return user

    async def profile(self, access_token: str) -> User:
        payload = decode_token(access_token)
        if payload:
            user = await self.user_repository.get_by_id(payload.get('user_id'))
        else:
            user = await self.user_repository.get_by_id(1)
        return user

    async def profile_edit(self, access_token: str, profile_schema: ProfileSchema) -> User:
        hashed_password = self.password_hasher(profile_schema.password)
        return await self.user_repository.profile_edit(access_token, profile_schema, hashed_password)

    async def chat_activate(self, user_id: int) -> None:
        return await self.user_repository.chat_activate(user_id)
