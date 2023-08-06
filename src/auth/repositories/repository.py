import datetime
from typing import Callable, Iterator

import passlib.hash
from fastapi import Response, Request
from jwt import ExpiredSignatureError
from sqlalchemy.orm import Session
from src.users.models import User
from src.auth.schemas import LoginScheme
import jwt
import config.settings as settings


class AuthRepository:

    def __init__(self, session_factory: Callable[..., Session]) -> None:
        self.session_factory = session_factory

    def login(self, login_scheme: LoginScheme) -> User:
        with self.session_factory() as session:
            user = session.query(User).filter(User.email == login_scheme.email).first()
            if not user:
                raise UserNotFoundError(login_scheme.email)
            else:
                if passlib.hash.pbkdf2_sha256.verify(login_scheme.password, user.password):
                    return user
                else:
                    return None


class NotFoundError(Exception):
    entity_name: str

    def __init__(self, entity_id):
        super().__init__(f"{self.entity_name} not found, id: {entity_id}")


class UserNotFoundError(NotFoundError):
    entity_name: str = "User"
