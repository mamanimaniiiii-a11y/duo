from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import PackPurchaseStatus
from app.schemas.common import ORMModel


class MentorPackCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10)
    price_dzd: int = Field(ge=0)
    duration_days: int = Field(ge=1)
    max_projects: int = Field(ge=1)
    features: list[str] = Field(default_factory=list)
    is_active: bool = True
    project_id: UUID | None = None


class MentorPackUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, min_length=10)
    price_dzd: int | None = Field(default=None, ge=0)
    duration_days: int | None = Field(default=None, ge=1)
    max_projects: int | None = Field(default=None, ge=1)
    features: list[str] | None = None
    is_active: bool | None = None
    project_id: UUID | None = None


class MentorPackPublic(ORMModel):
    id: UUID
    mentor_id: UUID
    project_id: UUID | None = None
    title: str
    description: str
    price_dzd: int
    duration_days: int
    max_projects: int
    features: list[str]
    is_active: bool


class PackPurchaseCreate(BaseModel):
    pack_id: UUID


class PackPurchasePublic(ORMModel):
    id: UUID
    pack_id: UUID
    apprenant_id: UUID
    mentor_id: UUID
    status: PackPurchaseStatus
    purchased_at: datetime | None = None
    expires_at: datetime | None = None
    amount_dzd: int
