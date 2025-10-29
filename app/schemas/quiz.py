from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class BaseConfigModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AnswerBase(BaseModel):
    text: str = Field(..., min_length=1)
    is_correct: bool


class AnswerCreate(AnswerBase):
    pass


class AnswerRead(AnswerBase, BaseConfigModel):
    id: UUID
    created_at: datetime
    updated_at: datetime


class QuestionBase(BaseModel):
    text: str = Field(..., min_length=1)


class QuestionCreate(QuestionBase):
    answers: List[AnswerCreate] = Field(..., min_length=2, max_length=4)


class QuestionRead(QuestionBase, BaseConfigModel):
    id: UUID
    answers: List[AnswerRead]
    created_at: datetime
    updated_at: datetime


class QuizBase(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    max_attempts_per_user: Optional[int] = Field(None, ge=1)


class QuizCreate(QuizBase):
    questions: List[QuestionCreate] = Field(..., min_length=2)


class QuizRead(QuizBase, BaseConfigModel):
    id: UUID
    company_id: UUID
    questions: List[QuestionRead]
    created_at: datetime
    updated_at: datetime


class QuizUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    max_attempts_per_user: Optional[int] = Field(None, ge=1)
    questions: Optional[List[QuestionCreate]] = Field(None, min_length=2)
