from app.models.quiz_attempt import QuizAttempt
from app.models.user_answer import UserAnswer
from app.repository.base import BaseRepository
from sqlalchemy import select, func
from uuid import UUID
from typing import Optional


class UserAnswerRepository(BaseRepository[UserAnswer]):
    def __init__(self, session):
        super().__init__(UserAnswer, session)

    async def get_total_answered_for_user(
        self, user_id: UUID, company_id: Optional[UUID] = None
    ) -> int:
        stmt = (
            select(func.count(self.model.id))
            .join(QuizAttempt, self.model.attempt_id == QuizAttempt.id)
            .where(QuizAttempt.user_id == user_id)
        )

        if company_id:
            stmt = stmt.where(QuizAttempt.company_id == company_id)

        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_total_correct_for_user(
        self, user_id: UUID, company_id: Optional[UUID] = None
    ) -> int:
        stmt = (
            select(func.count(self.model.id))
            .join(QuizAttempt, self.model.attempt_id == QuizAttempt.id)
            .where(QuizAttempt.user_id == user_id, self.model.is_correct == True)
        )

        if company_id:
            stmt = stmt.where(QuizAttempt.company_id == company_id)

        result = await self.session.execute(stmt)
        return result.scalar() or 0
