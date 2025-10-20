from pydantic import BaseModel


class BaseConfigModel(BaseModel):
    class Config:
        orm_mode = True
        from_attributes = True
