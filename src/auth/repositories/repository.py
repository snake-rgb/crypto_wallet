from typing import Callable
import passlib.hash
from asyncpg import UniqueViolationError
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.users.models import User
from src.auth.schemas import LoginScheme, RegisterSchema


class AuthRepository:

    def __init__(self, session_factory: Callable[..., AsyncSession]) -> None:
        self.session_factory = session_factory

    async def login(self, login_scheme: LoginScheme) -> User:
        async with self.session_factory() as session:
            result = await session.execute(select(User).where(User.email == login_scheme.email))
            user = result.scalar_one_or_none()
            if user is None:
                raise HTTPException(status_code=404, detail=f'Cant find user with email {login_scheme.email}')
            else:
                if passlib.hash.pbkdf2_sha256.verify(login_scheme.password, user.password):
                    return user
                else:
                    return None

    async def register(self, register_schema: RegisterSchema, hashed_password) -> User:
        async with self.session_factory() as session:
            try:
                user = User(**register_schema.model_dump(exclude=['password', 'confirm_password']),
                            password=hashed_password)
                session.add(user)
                await session.commit()
                return user
            except IntegrityError:
                raise HTTPException(status_code=400, detail='Email already exist')


class NotFoundError(Exception):
    entity_name: str

    def __init__(self, entity_id):
        super().__init__(f"{self.entity_name} not found, id: {entity_id}")


class UserNotFoundError(NotFoundError):
    entity_name: str = "User"
