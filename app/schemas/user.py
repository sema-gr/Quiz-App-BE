from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID
from app.schemas.base import BaseConfigModel


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


class UserRegister(BaseModel):
    email: EmailStr
    full_name: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(BaseConfigModel):
    id: UUID
    email: EmailStr
    full_name: str


class UserResponse(UserBase, BaseConfigModel):
    id: UUID


class UsersList(BaseModel):
    users: List[UserResponse]
