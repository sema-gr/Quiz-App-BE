import uuid
from typing import List
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from app.models.mixin import UUIDMixin, TimestampMixin


class Question(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "questions"

    quiz_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)

    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="questions")

    answers: Mapped[List["Answer"]] = relationship(
        "Answer", back_populates="question", cascade="all, delete-orphan"
    )
