import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enum_column import pg_enum
from app.models.enums import ListingStatus


class Listing(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Annonces de recrutement d'apprenants publiées par les mentors."""

    __tablename__ = "listings"

    mentor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    required_skills: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[ListingStatus] = mapped_column(
        pg_enum(ListingStatus, name="listing_status"), default=ListingStatus.DRAFT, nullable=False
    )
    applications_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    project = relationship("Project", back_populates="listings")
    applications = relationship("Application", back_populates="listing", cascade="all, delete-orphan")
