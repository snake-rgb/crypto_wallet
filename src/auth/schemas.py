from typing import List

from pydantic import BaseModel, Field, EmailStr


class LoginScheme(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = Field(default=False)



