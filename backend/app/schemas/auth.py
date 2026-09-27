from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import Locale, UserRole
from app.schemas.common import ORMModel


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=2, max_length=120)
    role: UserRole
    locale: Locale = Locale.FR
    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=30,
        description="Identifiant unique (généré automatiquement si omis)",
    )
    skills: list[str] = Field(default_factory=list, description="Compétences initiales (apprenant)")
    career_goal: str = Field(default="", description="Objectif de carrière (apprenant)")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserPublic(ORMModel):
    id: UUID
    email: EmailStr
    role: UserRole
    display_name: str
    avatar_url: str | None = None
    locale: Locale
    onboarding_completed: bool
