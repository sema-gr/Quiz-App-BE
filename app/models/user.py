from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.mixin import UUIDMixin, TimestampMixin


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    companies: Mapped[list["Company"]] = relationship(
        "Company", back_populates="owner", cascade="all, delete-orphan"
    )

    company_associations: Mapped[list["CompanyAssociation"]] = relationship(
        "CompanyAssociation",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="raise_on_sql",
    )

    performed_actions: Mapped[list["CompanyAction"]] = relationship(
        "CompanyAction",
        back_populates="performed_by",
        lazy="raise_on_sql",
    )
