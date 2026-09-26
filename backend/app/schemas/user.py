from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import BoostStatus, Locale, UserRole
from app.schemas.common import ORMModel, ScoreBreakdown


class UserUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=2, max_length=120)
    avatar_url: str | None = None
    locale: Locale | None = None


class ClientProfileUpdate(BaseModel):
    company_name: str | None = None
    phone: str | None = None


class MentorProfileUpdate(BaseModel):
    bio: str | None = None
    service_category_ids: list[UUID] | None = None
    availability_note: str | None = None


class ApprenantProfileUpdate(BaseModel):
    skills: list[str] | None = None
    career_goal: str | None = None


class OnboardingComplete(BaseModel):
    pass


class MentorProfilePublic(ORMModel):
    user_id: UUID
    bio: str
    service_category_ids: list[UUID]
    score: int
    is_certified: bool
    is_premium: bool
    boost_status: BoostStatus
    boost_expires_at: str | None = None
    availability_note: str | None = None


class ApprenantProfilePublic(ORMModel):
    user_id: UUID
    skills: list[str]
    career_goal: str
    score: int
    can_become_freelance: bool
    portfolio_project_ids: list[UUID]


class UserSummary(ORMModel):
    id: UUID
    display_name: str
    avatar_url: str | None = None


class MentorSummary(UserSummary):
    score: int
    is_certified: bool


class ApprenantSummary(UserSummary):
    score: int


class AccountResponse(ORMModel):
    id: UUID
    email: str
    role: UserRole
    display_name: str
    avatar_url: str | None = None
    locale: Locale
    onboarding_completed: bool
    client_profile: dict | None = None
    mentor_profile: MentorProfilePublic | None = None
    apprenant_profile: ApprenantProfilePublic | None = None
    score_breakdown: ScoreBreakdown | None = None
