from sqlalchemy import Column, DateTime, ForeignKey, Integer, LargeBinary, String, func
from database import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    yjs_state = Column(LargeBinary, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())