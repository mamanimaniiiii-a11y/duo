import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enum_column import pg_enum
from app.models.enums import BoostStatus

mentor_categories = Table(
    "mentor_categories",
    Base.metadata,
    Column("mentor_profile_id", UUID(as_uuid=True), ForeignKey("mentor_profiles.id"), primary_key=True),
    Column("category_id", UUID(as_uuid=True), ForeignKey("categories.id"), primary_key=True),
)


class ClientProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "client_profiles"
    __table_args__ = (UniqueConstraint("user_id", name="uq_client_profiles_user_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    company_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)

    user = relationship("User", back_populates="client_profile")


class MentorProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "mentor_profiles"
    __table_args__ = (UniqueConstraint("user_id", name="uq_mentor_profiles_user_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    bio: Mapped[str] = mapped_column(Text, default="", nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_certified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    boost_status: Mapped[BoostStatus] = mapped_column(
        pg_enum(BoostStatus, name="boost_status"), default=BoostStatus.INACTIVE, nullable=False
    )
    boost_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    availability_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    projects_completed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    apprentices_mentored_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    user = relationship("User", back_populates="mentor_profile")
    categories = relationship("Category", secondary=mentor_categories, back_populates="mentors")


class ApprenantProfile(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "apprenant_profiles"
    __table_args__ = (UniqueConstraint("user_id", name="uq_apprenant_profiles_user_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    skills: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    career_goal: Mapped[str] = mapped_column(Text, default="", nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    can_become_freelance: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    portfolio_project_ids: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    projects_completed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    user = relationship("User", back_populates="apprenant_profile")
