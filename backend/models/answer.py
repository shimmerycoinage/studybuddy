from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, func
from database import Base


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())