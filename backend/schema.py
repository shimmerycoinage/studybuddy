from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

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

class QuestionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    body: str = Field(min_length=1, pattern=r"\S")

class QuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    author_id: int
    body: str
    is_resolved: bool
    created_at: datetime

class AnswerCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    body: str = Field(min_length=1, pattern=r"\S")

class AnswerRead(BaseModel):
    id: int
    question_id: int
    body: str
    author_id: int
    author_name: str | None
    created_at: datetime

class MaterialRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    author_id: int
    original_name: str
    size_bytes: int
    created_at: datetime

class MaterialListItem(MaterialRead):
    author_name: str | None