from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status_code: int = Field(..., description="Status Code", example=200)
    detail: str = Field(..., description="Detail", example="ok")
    result: str = Field(..., description="Result", example="working")
