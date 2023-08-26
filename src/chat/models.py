import datetime

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy_utils import URLType

from src.core.database import Base


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, unique=True)
    text = Column(String)
    date = Column(DateTime(), default=datetime.datetime.utcnow())
    image = Column(URLType, default='')
    user_id = Column(Integer, ForeignKey('users.id'))
    # args  =  model name, table name
    user = relationship('User', backref="users")
