from fastapi import APIRouter, status
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get(
    "/",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    description="Check server",
)
async def health_check() -> HealthResponse:
    return HealthResponse(status_code=200, detail="ok", result="working")
