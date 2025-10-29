import uuid
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.mixin import TimestampMixin, UUIDMixin


class CompanyAssociation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "company_associations"

    role: Mapped[str] = mapped_column(nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    company: Mapped["Company"] = relationship("Company", back_populates="associations")
    user: Mapped["User"] = relationship("User", back_populates="company_associations")
