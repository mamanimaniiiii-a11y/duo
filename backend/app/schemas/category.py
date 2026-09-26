from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import LocalizedString, ORMModel


class CategoryCreate(BaseModel):
    slug: str = Field(min_length=2, max_length=80)
    name: LocalizedString
    sort_order: int = 0
    is_active: bool = True


class CategoryUpdate(BaseModel):
    name: LocalizedString | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class CategoryPublic(ORMModel):
    id: UUID
    slug: str
    name: LocalizedString
    is_active: bool
    sort_order: int
