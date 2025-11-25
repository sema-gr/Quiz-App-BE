from app.models.quiz_attempt import QuizAttempt
from app.repository.base import BaseRepository
from sqlalchemy import select, func
from uuid import UUID


class QuizAttemptRepository(BaseRepository[QuizAttempt]):
    def __init__(self, session):
        super().__init__(QuizAttempt, session)

    async def count_attempts_for_quiz(self, user_id: UUID, quiz_id: UUID) -> int:
        stmt = select(func.count(self.model.id)).where(
            self.model.user_id == user_id, self.model.quiz_id == quiz_id
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0
