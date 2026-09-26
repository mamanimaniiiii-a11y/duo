from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enum_column import pg_enum
from app.models.enums import Locale, UserRole


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(pg_enum(UserRole, name="user_role"), nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    locale: Mapped[Locale] = mapped_column(
        pg_enum(Locale, name="locale"), default=Locale.FR, nullable=False
    )
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    client_profile = relationship("ClientProfile", back_populates="user", uselist=False)
    mentor_profile = relationship("MentorProfile", back_populates="user", uselist=False)
    apprenant_profile = relationship("ApprenantProfile", back_populates="user", uselist=False)
