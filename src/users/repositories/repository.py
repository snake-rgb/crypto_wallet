from typing import Callable, Iterator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.dependencies.jwt_auth import decode_token
from src.users.models import User
from src.users.schemas import ProfileSchema


class UserRepository:
    def __init__(self, session_factory: Callable[..., AsyncSession]) -> None:
        self.session_factory = session_factory

    async def get_all(self) -> Iterator[User]:
        async with self.session_factory() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            return users

    async def get_by_id(self, user_id: int) -> User:
        async with self.session_factory() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                raise UserNotFoundError(user_id)
            return user

    async def delete_by_id(self, user_id: int) -> None:
        async with self.session_factory() as session:
            user = await session.get(User, user_id)
            if not user:
                raise UserNotFoundError(user_id)

            await session.delete(user)
            await session.commit()

    async def profile_edit(self, access_token: str, profile_schema: ProfileSchema, hashed_password: str) -> User:
        async with self.session_factory() as session:
            payload = decode_token(access_token)
            if payload:
                result = await session.execute(select(User).where(User.id == payload.get('user_id')))
                user = result.scalar_one()
            else:
                result = await session.execute(select(User).where(User.id == 1))
                user = result.scalar_one()

            update_data = profile_schema.dict()

            if hashed_password:
                user.password = hashed_password
            if update_data.get('username'):
                user.username = update_data.get('username')
            if update_data.get('profile_image') != '':
                user.profile_image = update_data.get('profile_image')

            await session.commit()
            await session.refresh(user)

            return user

    async def chat_activate(self, user_id: int) -> User:
        async with self.session_factory() as session:
            query = await session.execute(select(User).where(User.id == user_id))
            user = query.scalar_one()
            user.has_chat_access = True
            await session.commit()
            await session.refresh(user)
            return user

    async def get_online_users(self) -> list[User]:
        async with self.session_factory() as session:
            query = await session.execute(select(User).where(User.is_online))
            users = query.scalars().all()
            return users

    async def set_user_is_online(self, user_id: int, status: bool) -> User:
        async with self.session_factory() as session:
            query = await session.execute(select(User).where(User.id == user_id))
            user = query.scalar_one()
            user.is_online = status
            await session.commit()
            await session.refresh(user)
            return user


class NotFoundError(Exception):
    entity_name: str

    def __init__(self, entity_id):
        super().__init__(f"{self.entity_name} not found, id: {entity_id}")


class UserNotFoundError(NotFoundError):
    entity_name: str = "User"
