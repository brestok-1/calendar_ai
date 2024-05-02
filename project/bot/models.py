from sqlalchemy import Column, Integer, Text, VARCHAR, DateTime
from sqlalchemy.sql.functions import now

from project.database import Base


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=now())
    role = Column(VARCHAR(9))
    content = Column(Text)

    def __init__(self, role, content):
        self.role = role
        self.content = content
