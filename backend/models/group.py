from sqlalchemy import Column, Integer, String, Text
from database import Base


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    invite_code = Column(String, nullable=False, unique=True)