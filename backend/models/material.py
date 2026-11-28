from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String, false, func
from database import Base


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_name = Column(String, nullable=False)
    storage_key = Column(String, nullable=False, unique=True)
    size_bytes = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    delete_pending = Column(Boolean, nullable=False, server_default=false())