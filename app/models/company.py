from typing import TYPE_CHECKING
import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from app.models.mixin import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from .user import User
    from .company_associationand_actions import CompanyAssociation


class Company(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    is_visible: Mapped[bool] = mapped_column(default=True)

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    owner: Mapped["User"] = relationship("User", back_populates="companies")
    associations: Mapped[list["CompanyAssociation"]] = relationship(
        "CompanyAssociation",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="raise_on_sql",
    )
