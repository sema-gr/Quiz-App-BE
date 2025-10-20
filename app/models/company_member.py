from typing import TYPE_CHECKING
import enum
import uuid
from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.mixin import UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from .user import User
    from .company import Company


class MembershipStatus(enum.Enum):
    MEMBER = "member"
    INVITED = "invited"
    REQUESTED = "requested"


class CompanyMember(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "company_members"

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
        default=MembershipStatus.REQUESTED,
    )

    company: Mapped["Company"] = relationship("Company", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="memberships")
