from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class LocalizedString(BaseModel):
    fr: str
    en: str
    ar: str


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class ScoreBreakdown(BaseModel):
    total: int = Field(ge=0, le=100)
    projects_completed: int = 0
    apprentices_mentored: int | None = None
    average_rating: float = 0.0


class MessageResponse(BaseModel):
    message: str


class TimestampSchema(BaseModel):
    created_at: datetime
    updated_at: datetime
