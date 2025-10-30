from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.schemas.base import BaseConfigModel


class UserAnswerSubmit(BaseModel):
    question_id: UUID
    selected_answer_ids: List[UUID] = Field(..., min_length=1)


class QuizSubmit(BaseModel):
    answers: List[UserAnswerSubmit] = Field(..., min_length=1)


class QuizResultRead(BaseConfigModel):
    attempt_id: UUID
    quiz_id: UUID
    company_id: UUID
    score: int
    total_questions: int
    percentage: float
    submitted_at: datetime


class UserStatsRead(BaseModel):
    user_id: UUID
    company_id: Optional[UUID] = None
    total_correct_answers: int
    total_answered_questions: int
    average_score_percentage: float
