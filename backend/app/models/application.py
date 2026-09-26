import uuid

from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enum_column import pg_enum
from app.models.enums import ApplicationStatus


class Application(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "applications"

    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    apprenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[ApplicationStatus] = mapped_column(
        pg_enum(ApplicationStatus, name="application_status"),
        default=ApplicationStatus.PENDING,
        nullable=False,
    )
    cover_letter: Mapped[str] = mapped_column(Text, nullable=False)
    ai_match_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    listing = relationship("Listing", back_populates="applications")
