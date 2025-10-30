from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends
from app.models.user import User
from app.schemas.quiz import QuizCreate, QuizRead, QuizUpdate
from app.schemas.quiz_submission import QuizResultRead, QuizSubmit
from app.services.quiz import QuizService
from app.core.dependencies import get_current_user, get_quiz_service

router = APIRouter(prefix="/companies/{company_id}/quizzes", tags=["Quizzes"])


@router.post("/", response_model=QuizRead)
async def create_quiz(
    company_id: UUID,
    quiz_data: QuizCreate,
    user_id: User = Depends(get_current_user),
    service: QuizService = Depends(get_quiz_service),
):
    return await service.create_quiz(user_id.id, company_id, quiz_data)


@router.put("/{quiz_id}", response_model=QuizRead)
async def update_quiz(
    company_id: UUID,
    quiz_id: UUID,
    quiz_data: QuizUpdate,
    user_id: User = Depends(get_current_user),
    service: QuizService = Depends(get_quiz_service),
):
    return await service.update_quiz(user_id.id, company_id, quiz_id, quiz_data)


@router.delete("/{quiz_id}", status_code=204)
async def delete_quiz(
    company_id: UUID,
    quiz_id: UUID,
    user_id: User = Depends(get_current_user),
    service: QuizService = Depends(get_quiz_service),
):
    await service.delete_quiz(user_id.id, company_id, quiz_id)


@router.get("/{quiz_id}", response_model=QuizRead)
async def get_quiz(
    company_id: UUID,
    quiz_id: UUID,
    user_id: User = Depends(get_current_user),
    service: QuizService = Depends(get_quiz_service),
):
    return await service.get_quiz(user_id.id, company_id, quiz_id)


@router.get("/", response_model=List[QuizRead])
async def list_quizzes(
    company_id: UUID,
    user_id: User = Depends(get_current_user),
    service: QuizService = Depends(get_quiz_service),
):
    return await service.list_quizzes_for_company(user_id.id, company_id)


@router.post("/{quiz_id}/submit", response_model=QuizResultRead)
async def submit_quiz(
    company_id: UUID,
    quiz_id: UUID,
    submission: QuizSubmit,
    current_user: User = Depends(get_current_user),
    service: QuizService = Depends(get_quiz_service),
):
    return await service.submit_quiz(
        user_id=current_user.id,
        company_id=company_id,
        quiz_id=quiz_id,
        submission=submission,
    )
