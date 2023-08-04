from sqlalchemy import Column
from sqlalchemy.types import String, Integer
from sqlalchemy_utils import EmailType, URLType, PasswordType

from src.core.database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, unique=True)
    username = Column(String)
    email = Column(EmailType, unique=True)
    password = Column(String)
    profile_image = Column(URLType)

    def __repr__(self):
        return (
            f'id - {str(self.id)}\n'
            f'Username - {self.username}\n'
            f'Email - {self.email}\n'
            f'Password - {self.password}\n'
            f'Profile image - {self.profile_image}\n'
        )
