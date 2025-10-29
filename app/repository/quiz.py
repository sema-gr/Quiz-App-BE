from uuid import UUID
from typing import Optional, Sequence
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.answer import Answer
from app.models.quiz import Quiz
from app.models.question import Question
from app.repository.base import BaseRepository


class QuizRepository(BaseRepository[Quiz]):
    def __init__(self, session: AsyncSession):
        super().__init__(Quiz, session)

    async def get_by_id_with_details(self, quiz_id: UUID) -> Optional[Quiz]:
        stmt = (
            select(self.model)
            .where(self.model.id == quiz_id)
            .options(selectinload(self.model.questions).selectinload(Question.answers))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all_for_company(
        self, company_id: UUID, skip: int = 0, limit: int = 10
    ) -> Sequence[Quiz]:
        stmt = (
            select(self.model)
            .where(self.model.company_id == company_id)
            .options(selectinload(self.model.questions).selectinload(Question.answers))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def delete_by_company(self, company_id: UUID):
        await self.session.execute(
            delete(self.model).where(self.model.company_id == company_id)
        )


class QuestionRepository(BaseRepository[Question]):
    def __init__(self, session: AsyncSession):
        super().__init__(Question, session)


class AnswerRepository(BaseRepository[Answer]):
    def __init__(self, session: AsyncSession):
        super().__init__(Answer, session)
