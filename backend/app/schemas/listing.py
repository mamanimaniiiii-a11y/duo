from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import ApplicationStatus, ListingStatus
from app.schemas.common import ORMModel


class ListingCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10)
    required_skills: list[str] = Field(default_factory=list)
    project_id: UUID | None = None


class ListingUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, min_length=10)
    required_skills: list[str] | None = None
    project_id: UUID | None = None
    status: ListingStatus | None = None


class ListingPublic(ORMModel):
    id: UUID
    mentor_id: UUID
    title: str
    description: str
    required_skills: list[str]
    project_id: UUID | None = None
    status: ListingStatus
    applications_count: int
    created_at: datetime
    updated_at: datetime


class ApplicationCreate(BaseModel):
    cover_letter: str = Field(min_length=10)


class ApplicationUpdate(BaseModel):
    status: ApplicationStatus


class ApplicationPublic(ORMModel):
    id: UUID
    listing_id: UUID
    apprenant_id: UUID
    status: ApplicationStatus
    cover_letter: str
    ai_match_score: int | None = None
    created_at: datetime
    updated_at: datetime
