from uuid import UUID
from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user, get_quiz_service
from app.models.user import User
from app.schemas.quiz_submission import UserStatsRead
from app.services.quiz import QuizService

router = APIRouter(prefix="/profile", tags=["ProfileStats"])


@router.get("/me/stats", response_model=UserStatsRead)
async def get_my_overall_stats(
    current_user: User = Depends(get_current_user),
    service: QuizService = Depends(get_quiz_service),
):
    return await service.get_user_stats(user_id=current_user.id)


@router.get("/me/stats/companies/{company_id}", response_model=UserStatsRead)
async def get_my_company_stats(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    service: QuizService = Depends(get_quiz_service),
):
    return await service.get_user_stats(user_id=current_user.id, company_id=company_id)
