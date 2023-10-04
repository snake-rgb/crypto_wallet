from typing import List, Optional

from pydantic import BaseModel, ValidationError, EmailStr, validator
from email_validator import validate_email, EmailNotValidError
import re


class EmailSchema(BaseModel):
    email: List[EmailStr]


class ProfileSchema(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    confirm_password: Optional[str] = None
    profile_image: Optional[str] = None

    @validator('password')
    @classmethod
    def validate_password(cls, password: str):
        password_pattern = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,}$"

        if password is '':
            return None

        if not re.match(password_pattern, password) or len(password) > 20:
            raise ValueError(f'Password must contain minimal 8 symbols '
                             f'Password must contain max 20 symbols '
                             f'Password must contain 1 small letter '
                             f'Password must contain 1 capital letter '
                             )
        else:
            return password

    @validator('confirm_password')
    @classmethod
    def validate_confirm_password(cls, confirm_password: str, values):
        if confirm_password is '' and values.get('password') is None:
            return None

        if confirm_password == values.get('password'):
            return confirm_password
        else:
            raise ValueError('Password must be equal')
