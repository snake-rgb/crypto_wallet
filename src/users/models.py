from sqladmin import ModelView
from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import String, Integer, Boolean
from sqlalchemy_utils import EmailType, URLType, PasswordType
from src.core.database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, unique=True)
    username = Column(String)
    email = Column(EmailType, unique=True)
    password = Column(String)
    profile_image = Column(
        URLType,
        default='https://cryptowalletbucket.s3.eu-north-1.amazonaws.com/images/standart_image.jpg')
    is_active = Column(Boolean, default=True)
    has_chat_access = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.email, User.password, User.profile_image, User.is_active,
                   User.has_chat_access, User.is_admin]
