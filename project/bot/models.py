from sqlalchemy import Column, Integer, Text, VARCHAR, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import now

from project.database import Base


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role = Column(VARCHAR(9))
    content = Column(Text)
    time_created = Column(DateTime, default=now())

    chat_id = Column(Integer, ForeignKey("chats.id"))
    chat = relationship('Chat', back_populates='messages')


class Chat(Base):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    messages = relationship('Message', back_populates='chat')

    user = relationship('User', back_populates='chats')
    user_id = Column(Integer, ForeignKey('users.id'))
