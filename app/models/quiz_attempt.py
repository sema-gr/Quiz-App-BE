import uuid
from typing import List
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from app.models.mixin import UUIDMixin, TimestampMixin


class QuizAttempt(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "quiz_attempts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    quiz_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )

    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship()
    quiz: Mapped["Quiz"] = relationship()
    company: Mapped["Company"] = relationship()

    user_answers: Mapped[List["UserAnswer"]] = relationship(
        "UserAnswer", back_populates="attempt", cascade="all, delete-orphan"
    )
