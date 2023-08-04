from typing import Callable
from sqlalchemy.orm import Session
from src.users.models import User
from src.users.schemas import UserForm
from src.users.services.repository import UserRepository
from email_validator import validate_email, EmailNotValidError


class UserService:

    def __init__(self, user_repository: UserRepository, session_factory: Callable[..., Session],
                 password_hasher: Callable[[str], str]) -> None:
        self.user_repository = user_repository
        self.session_factory = session_factory
        self.password_hasher = password_hasher

    def get_users(self):
        return self.user_repository.get_all()

    def get_user_by_id(self, user_id: int):
        return self.user_repository.get_by_id(user_id)

    def delete_user_by_id(self, user_id: int):
        return self.user_repository.delete_by_id(user_id)

    def create_user(self, user_form: UserForm):
        hashed_password = self.password_hasher(user_form.password)
        self.user_repository.add(user_form, hashed_password=hashed_password)
        return None
