import datetime
from typing import Callable, Iterator
from sqlalchemy.orm import Session

from src.auth.dependencies.jwt_auth import decode_token
from src.users.models import User
from src.users.schemas import UserForm, ProfileSchema
import jwt
import config.settings as settings


class UserRepository:
    def __init__(self, session_factory: Callable[..., Session]) -> None:
        self.session_factory = session_factory

    async def get_all(self) -> Iterator[User]:
        with self.session_factory() as session:
            return session.query(User).all()

    async def get_by_id(self, user_id: int) -> User:
        with self.session_factory() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                raise UserNotFoundError(user_id)
            return user

    async def delete_by_id(self, user_id: int) -> None:
        with self.session_factory() as session:
            # entity - сущность
            entity: User = session.query(User).filter(User.id == user_id).first()
            if not entity:
                raise UserNotFoundError(user_id)
            session.delete(entity)
            session.commit()

    async def register(self, user_form: UserForm, hashed_password) -> User:
        with self.session_factory() as session:
            user = User(**user_form.model_dump(exclude=['password', 'confirm_password']), password=hashed_password)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    async def profile_edit(self, access_token: str, profile_schema: ProfileSchema, hashed_password: str):
        with self.session_factory() as session:
            payload = decode_token(access_token)
            if payload:
                user = session.query(User).filter(User.id == payload.get('user_id')).first()
            else:
                user = session.query(User).filter(User.id == 1).one()
            update_data = profile_schema.model_dump()
            user.password = hashed_password
            user.username = update_data.get('username')
            session.commit()
            session.refresh(user)
            return user


class NotFoundError(Exception):
    entity_name: str

    def __init__(self, entity_id):
        super().__init__(f"{self.entity_name} not found, id: {entity_id}")


class UserNotFoundError(NotFoundError):
    entity_name: str = "User"
