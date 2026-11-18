from pydantic import BaseModel, EmailStr, Field
from typing import Literal

class UserCreate(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr = Field(min_length=1)
    password: str = Field(min_length=8)
class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
class UserLogin(BaseModel):
    email: EmailStr
    password: str
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
class GroupCreate(BaseModel):
    name: str = Field(min_length=1, pattern=r"\S")
    description: str | None = None
class GroupCreated(BaseModel):
    id: int
    name: str
    description: str | None
    invite_code: str
    member_count: int
class GroupListItem(BaseModel):
    id: int
    name: str
    description: str | None
    member_count: int
class GroupJoin(BaseModel):
    invite_code: str = Field(min_length=1)
class GroupDetail(GroupListItem):
    my_role: Literal["owner", "member"]