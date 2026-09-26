import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enum_column import pg_enum
from app.models.enums import SubscriptionStatus


class BoostOption(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "boost_options"

    label_fr: Mapped[str] = mapped_column(String(120), nullable=False)
    label_en: Mapped[str] = mapped_column(String(120), nullable=False)
    label_ar: Mapped[str] = mapped_column(String(120), nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    price_dzd: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    subscriptions = relationship("BoostSubscription", back_populates="option")


class PremiumPlan(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "premium_plans"

    label_fr: Mapped[str] = mapped_column(String(120), nullable=False)
    label_en: Mapped[str] = mapped_column(String(120), nullable=False)
    label_ar: Mapped[str] = mapped_column(String(120), nullable=False)
    price_dzd: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    benefits: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    subscriptions = relationship("PremiumSubscription", back_populates="plan")


class BoostSubscription(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "boost_subscriptions"

    mentor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    boost_option_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("boost_options.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[SubscriptionStatus] = mapped_column(
        pg_enum(SubscriptionStatus, name="subscription_status"),
        default=SubscriptionStatus.PENDING_PAYMENT,
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    amount_dzd: Mapped[int] = mapped_column(Integer, nullable=False)

    option = relationship("BoostOption", back_populates="subscriptions")


class PremiumSubscription(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "premium_subscriptions"

    mentor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("premium_plans.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[SubscriptionStatus] = mapped_column(
        pg_enum(SubscriptionStatus, name="subscription_status"),
        default=SubscriptionStatus.PENDING_PAYMENT,
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    amount_dzd: Mapped[int] = mapped_column(Integer, nullable=False)

    plan = relationship("PremiumPlan", back_populates="subscriptions")
