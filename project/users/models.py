from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from project.database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    chats = relationship('Chat', back_populates='user')