from typing import Optional

from pydantic import BaseModel


class MessageSchema(BaseModel):
    text: str
    image: Optional[str] = ''
