from pydantic import BaseModel, EmailStr, Field

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