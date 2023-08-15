from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import String, Integer, Boolean
from sqlalchemy_utils import EmailType, URLType, PasswordType
import json
from sqlalchemy import TypeDecorator, Unicode
from src.core.database import Base



class Json(TypeDecorator):
    impl = Unicode

    def process_bind_param(self, value, engine):
        return json.dumps(value)

    def process_result_value(self, value, engine):
        if value is None:
            return None

        return json.loads(value)



class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, unique=True)
    username = Column(String)
    email = Column(EmailType, unique=True)
    password = Column(String)
    profile_image = Column(URLType)
    is_active = Column(Boolean, default=True)
    has_chat_access = Column(Boolean, default=False)

    def __repr__(self):
        return (
            f'id - {str(self.id)}\n'
            f'Username - {self.username}\n'
            f'Email - {self.email}\n'
            f'Password - {self.password}\n'
            f'Profile image - {self.profile_image}\n'
            f'Is active - {self.is_active}\n'
            f'Has chat access - {self.is_active}\n'
        )
