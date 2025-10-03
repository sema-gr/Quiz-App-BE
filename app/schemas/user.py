from pydantic import BaseModel, EmailStr
from typing import Optional, List


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True


class UsersList(BaseModel):
    users: List[UserResponse]
