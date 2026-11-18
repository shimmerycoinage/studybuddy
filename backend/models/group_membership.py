from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String
from database import Base


class GroupMembership(Base):
    __tablename__ = "group_memberships"

    group_id = Column(Integer, ForeignKey("groups.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role = Column(String, nullable=False, server_default="member")

    __table_args__ = (
        CheckConstraint(
            "role IN ('owner', 'member')",
            name="ck_group_memberships_role",
        ),
    )