from pydantic import BaseModel


class HealthResponse(BaseModel):
    status_code: int
    detail: str
    result: str
