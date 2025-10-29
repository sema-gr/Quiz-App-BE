from typing import Optional
import uuid
from sqlalchemy import ForeignKey, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.enum import MembershipAction, MembershipStatus
from app.models.mixin import TimestampMixin, UUIDMixin


class CompanyAction(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "company_actions"

    association_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("company_associations.id", ondelete="CASCADE"),
        nullable=False,
    )
    action_type: Mapped[MembershipAction] = mapped_column(
        Enum(MembershipAction, name="action_type"),
        nullable=False,
    )
    performed_by_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[MembershipStatus] = mapped_column(
        Enum(MembershipStatus, name="membership_status"),
        nullable=False,
        default=MembershipStatus.PENDING,
    )

    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    performed_by: Mapped[Optional["User"]] = relationship("User")
