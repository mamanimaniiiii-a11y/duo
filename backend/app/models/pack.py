import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enum_column import pg_enum
from app.models.enums import PackPurchaseStatus


class MentorPack(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "mentor_packs"

    mentor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price_dzd: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    max_projects: Mapped[int] = mapped_column(Integer, nullable=False)
    features: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True
    )

    purchases = relationship("PackPurchase", back_populates="pack", cascade="all, delete-orphan")
    project = relationship("Project", backref="mentor_packs")


class PackPurchase(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "pack_purchases"

    pack_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("mentor_packs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    apprenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    mentor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[PackPurchaseStatus] = mapped_column(
        pg_enum(PackPurchaseStatus, name="pack_purchase_status"),
        default=PackPurchaseStatus.PENDING_PAYMENT,
        nullable=False,
    )
    purchased_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    amount_dzd: Mapped[int] = mapped_column(Integer, nullable=False)

    pack = relationship("MentorPack", back_populates="purchases")
