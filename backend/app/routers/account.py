from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.deps import CurrentUser, DbSession
from app.models.enums import UserRole
from app.models.profile import ApprenantProfile, ClientProfile, MentorProfile
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.user import (
    AccountResponse,
    ApprenantProfileUpdate,
    ClientProfileUpdate,
    MentorProfileUpdate,
    OnboardingComplete,
    UserUpdate,
)
from app.services.score_service import get_score_breakdown_for_user
from app.services.serializers import account_to_response

router = APIRouter(prefix="/account", tags=["Account"])


@router.get("", response_model=AccountResponse)
def get_account(db: DbSession, current_user: CurrentUser) -> AccountResponse:
    """Page /account — profil et paramètres."""
    client_profile = None
    mentor_profile = None
    apprenant_profile = None

    if current_user.role == UserRole.CLIENT:
        client_profile = db.scalar(
            select(ClientProfile).where(ClientProfile.user_id == current_user.id)
        )
    elif current_user.role == UserRole.MENTOR:
        mentor_profile = db.scalar(
            select(MentorProfile).where(MentorProfile.user_id == current_user.id)
        )
    elif current_user.role == UserRole.APPRENANT:
        apprenant_profile = db.scalar(
            select(ApprenantProfile).where(ApprenantProfile.user_id == current_user.id)
        )

    score = get_score_breakdown_for_user(db, current_user)
    return account_to_response(
        current_user, client_profile, mentor_profile, apprenant_profile, score
    )


@router.patch("", response_model=AccountResponse)
def update_account(
    payload: UserUpdate, db: DbSession, current_user: CurrentUser
) -> AccountResponse:
    if payload.display_name is not None:
        current_user.display_name = payload.display_name
    if payload.avatar_url is not None:
        current_user.avatar_url = payload.avatar_url
    if payload.locale is not None:
        current_user.locale = payload.locale
    db.commit()
    db.refresh(current_user)
    return get_account(db, current_user)


@router.patch("/client-profile", response_model=AccountResponse)
def update_client_profile(
    payload: ClientProfileUpdate, db: DbSession, current_user: CurrentUser
) -> AccountResponse:
    if current_user.role != UserRole.CLIENT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rôle client requis")
    profile = db.scalar(select(ClientProfile).where(ClientProfile.user_id == current_user.id))
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profil client introuvable")
    if payload.company_name is not None:
        profile.company_name = payload.company_name
    if payload.phone is not None:
        profile.phone = payload.phone
    db.commit()
    return get_account(db, current_user)


@router.patch("/mentor-profile", response_model=AccountResponse)
def update_mentor_profile(
    payload: MentorProfileUpdate, db: DbSession, current_user: CurrentUser
) -> AccountResponse:
    if current_user.role != UserRole.MENTOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rôle mentor requis")
    profile = db.scalar(select(MentorProfile).where(MentorProfile.user_id == current_user.id))
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profil mentor introuvable")
    if payload.bio is not None:
        profile.bio = payload.bio
    if payload.availability_note is not None:
        profile.availability_note = payload.availability_note
    if payload.service_category_ids is not None:
        from app.models.category import Category

        categories = db.scalars(
            select(Category).where(Category.id.in_(payload.service_category_ids))
        ).all()
        profile.categories = list(categories)
    db.commit()
    return get_account(db, current_user)


@router.patch("/apprenant-profile", response_model=AccountResponse)
def update_apprenant_profile(
    payload: ApprenantProfileUpdate, db: DbSession, current_user: CurrentUser
) -> AccountResponse:
    if current_user.role != UserRole.APPRENANT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rôle apprenant requis")
    profile = db.scalar(
        select(ApprenantProfile).where(ApprenantProfile.user_id == current_user.id)
    )
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profil apprenant introuvable")
    if payload.skills is not None:
        profile.skills = payload.skills
    if payload.career_goal is not None:
        profile.career_goal = payload.career_goal
    db.commit()
    return get_account(db, current_user)


@router.post("/onboarding/complete", response_model=MessageResponse)
def complete_onboarding(db: DbSession, current_user: CurrentUser, _: OnboardingComplete) -> MessageResponse:
    """Pages /client|mentor|apprenant/onboarding."""
    current_user.onboarding_completed = True
    db.commit()
    return MessageResponse(message="Onboarding terminé")
