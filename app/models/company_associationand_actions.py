from __future__ import annotations
from typing import Optional
import uuid
from sqlalchemy import ForeignKey, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.enum import MembershipAction, MembershipStatus
from app.models.mixin import UUIDMixin, TimestampMixin


class CompanyAssociation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "company_associations"

    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[MembershipStatus] = mapped_column(
        Enum(MembershipStatus, name="membership_status"),
        nullable=False,
        default=MembershipStatus.PENDING,
    )

    company: Mapped["Company"] = relationship("Company", back_populates="associations")
    user: Mapped["User"] = relationship("User", back_populates="company_associations")

    actions: Mapped[list[CompanyAction]] = relationship(
        "CompanyAction", back_populates="association", cascade="all, delete-orphan"
    )


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
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    association: Mapped[CompanyAssociation] = relationship(
        "CompanyAssociation", back_populates="actions"
    )
    performed_by: Mapped[Optional["User"]] = relationship("User")
