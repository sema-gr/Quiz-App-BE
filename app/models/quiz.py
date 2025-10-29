import uuid
from typing import List, Optional
from sqlalchemy import String, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from app.models.mixin import UUIDMixin, TimestampMixin


class Quiz(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "quizzes"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    max_attempts_per_user: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    questions: Mapped[List["Question"]] = relationship(
        "Question", back_populates="quiz", cascade="all, delete-orphan"
    )
