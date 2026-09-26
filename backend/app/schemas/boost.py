from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import SubscriptionStatus
from app.schemas.common import LocalizedString, ORMModel


class BoostOptionCreate(BaseModel):
    label: LocalizedString
    duration_days: int = Field(ge=1)
    price_dzd: int = Field(ge=0)
    is_active: bool = True


class PremiumPlanCreate(BaseModel):
    label: LocalizedString
    price_dzd: int = Field(ge=0)
    duration_days: int = Field(ge=1)
    benefits: list[str] = Field(default_factory=list)
    is_active: bool = True


class BoostOptionPublic(ORMModel):
    id: UUID
    label: LocalizedString
    duration_days: int
    price_dzd: int
    is_active: bool


class PremiumPlanPublic(ORMModel):
    id: UUID
    label: LocalizedString
    price_dzd: int
    duration_days: int
    benefits: list[str]
    is_active: bool


class BoostSubscribeRequest(BaseModel):
    boost_option_id: UUID


class PremiumSubscribeRequest(BaseModel):
    plan_id: UUID


class SubscriptionPublic(ORMModel):
    id: UUID
    status: SubscriptionStatus
    started_at: datetime | None = None
    expires_at: datetime | None = None
    amount_dzd: int
