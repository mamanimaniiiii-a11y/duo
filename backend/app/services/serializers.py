from uuid import UUID

from app.models.category import Category
from app.models.profile import ApprenantProfile, ClientProfile, MentorProfile
from app.models.user import User
from app.schemas.category import CategoryPublic
from app.schemas.common import LocalizedString, ScoreBreakdown
from app.schemas.user import (
    AccountResponse,
    ApprenantProfilePublic,
    ApprenantSummary,
    MentorProfilePublic,
    MentorSummary,
    UserSummary,
)


def category_to_public(category: Category) -> CategoryPublic:
    return CategoryPublic(
        id=category.id,
        slug=category.slug,
        name=LocalizedString(fr=category.name_fr, en=category.name_en, ar=category.name_ar),
        is_active=category.is_active,
        sort_order=category.sort_order,
    )


def user_to_summary(user: User) -> UserSummary:
    return UserSummary(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
    )


def mentor_to_summary(user: User, profile: MentorProfile | None = None) -> MentorSummary:
    return MentorSummary(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        skills=profile.skills or [] if profile else [],
        score=profile.score if profile else 0,
        is_certified=profile.is_certified if profile else False,
    )


def apprenant_to_summary(user: User, profile: ApprenantProfile | None = None) -> ApprenantSummary:
    return ApprenantSummary(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        score=profile.score if profile else 0,
    )


def mentor_profile_to_public(profile: MentorProfile) -> MentorProfilePublic:
    return MentorProfilePublic(
        user_id=profile.user_id,
        bio=profile.bio,
        service_category_ids=[cat.id for cat in profile.categories],
        skills=profile.skills or [],
        score=profile.score,
        is_certified=profile.is_certified,
        is_premium=profile.is_premium,
        boost_status=profile.boost_status,
        boost_expires_at=profile.boost_expires_at.isoformat() if profile.boost_expires_at else None,
        availability_note=profile.availability_note,
    )


def apprenant_profile_to_public(profile: ApprenantProfile) -> ApprenantProfilePublic:
    return ApprenantProfilePublic(
        user_id=profile.user_id,
        skills=profile.skills or [],
        career_goal=profile.career_goal,
        score=profile.score,
        can_become_freelance=profile.can_become_freelance,
        portfolio_project_ids=[UUID(str(pid)) for pid in (profile.portfolio_project_ids or [])],
    )


def account_to_response(
    user: User,
    client_profile: ClientProfile | None = None,
    mentor_profile: MentorProfile | None = None,
    apprenant_profile: ApprenantProfile | None = None,
    score_breakdown: ScoreBreakdown | None = None,
) -> AccountResponse:
    return AccountResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        role=user.role,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        locale=user.locale,
        onboarding_completed=user.onboarding_completed,
        client_profile={
            "company_name": client_profile.company_name,
            "phone": client_profile.phone,
        }
        if client_profile
        else None,
        mentor_profile=mentor_profile_to_public(mentor_profile) if mentor_profile else None,
        apprenant_profile=apprenant_profile_to_public(apprenant_profile) if apprenant_profile else None,
        score_breakdown=score_breakdown,
    )
