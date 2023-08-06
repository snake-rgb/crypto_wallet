from typing import List, Optional

from pydantic import BaseModel, field_validator, ValidationError, EmailStr
from email_validator import validate_email, EmailNotValidError
import re

from pydantic_core.core_schema import FieldValidationInfo


class UserForm(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str
    profile_image: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, email):
        try:
            validate_email(email)
            return email
        except ValidationError as e:
            print(e)

    @field_validator('password')
    @classmethod
    def validate_password(cls, password: str):
        password_pattern = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,}$"
        if not re.match(password_pattern, password) or len(password) > 20:
            raise ValueError(f'Password must contain minimal 8 symbols '
                             f'Password must contain max 20 symbols '
                             f'Password must contain 1 small letter '
                             f'Password must contain 1 capital letter '
                             )
        else:
            return password

    @field_validator('confirm_password')
    @classmethod
    def validate_confirm_password(cls, confirm_password: str, values: FieldValidationInfo):
        data = values.data
        if confirm_password == data.get('password'):
            return confirm_password
        else:
            raise ValueError('Password must be equal')


class EmailSchema(BaseModel):
    email: List[EmailStr]


class ProfileSchema(BaseModel):
    username: str
    password: Optional[str] = None
    confirm_password: Optional[str] = None
    profile_image: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, password: str):
        password_pattern = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,}$"

        if password is None:
            return None

        if not re.match(password_pattern, password) or len(password) > 20:
            raise ValueError(f'Password must contain minimal 8 symbols '
                             f'Password must contain max 20 symbols '
                             f'Password must contain 1 small letter '
                             f'Password must contain 1 capital letter '
                             )
        else:
            return password

    @field_validator('confirm_password')
    @classmethod
    def validate_confirm_password(cls, confirm_password: str, values: FieldValidationInfo):
        data = values.data
        if confirm_password is None:
            return None
        if confirm_password == data.get('password'):
            return confirm_password
        else:
            raise ValueError('Password must be equal')
