from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import ReviewType
from app.schemas.common import ORMModel


class ReviewCreate(BaseModel):
    to_user_id: UUID
    project_id: UUID | None = None
    rating: int = Field(ge=1, le=5)
    comment: str = Field(default="", max_length=2000)
    type: ReviewType


class ReviewPublic(ORMModel):
    id: UUID
    from_user_id: UUID
    to_user_id: UUID
    project_id: UUID | None = None
    rating: int
    comment: str
    type: ReviewType
    created_at: datetime
