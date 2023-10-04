import re
from typing import List, Optional

from email_validator import validate_email
from pydantic import BaseModel, Field, EmailStr, ValidationError, validator


class LoginScheme(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = Field(default=False)


class RegisterSchema(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str
    profile_image: Optional[str] = None

    @validator('email')
    @classmethod
    def validate_email(cls, email):
        try:
            validate_email(email)
            return email
        except ValidationError as e:
            print(e)

    @validator('password')
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

    @validator('confirm_password')
    @classmethod
    def validate_confirm_password(cls, confirm_password: str, values):

        if confirm_password == values.get('password'):
            return confirm_password
        else:
            raise ValueError('Password must be equal')
