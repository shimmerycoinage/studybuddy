from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text, false, func
from database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    is_resolved = Column(Boolean, nullable=False, server_default=false())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())