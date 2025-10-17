from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from app.schemas.base import BaseConfigModel


class CompanyBase(BaseConfigModel):
    name: str
    description: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_visible: Optional[bool] = None


class CompanyRead(CompanyBase):
    id: UUID
    is_visible: bool
    owner_id: UUID
