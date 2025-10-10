from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID


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


class UserRead(BaseModel):
    id: UUID
    email: str
    full_name: str

    class Config:
        orm_mode = True


class UserResponse(UserBase):
    id: UUID

    class Config:
        from_attributes = True


class UsersList(BaseModel):
    users: List[UserResponse]
