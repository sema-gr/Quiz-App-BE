from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.models.mixin import TimestampMixin, UUIDMixin
from sqlalchemy.orm import relationship


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    companies = relationship(
        "Company", back_populates="owner", cascade="all, delete-orphan"
    )
