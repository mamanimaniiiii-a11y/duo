from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select

from app.core.deps import DbSession
from app.models.category import Category
from app.models.enums import ListingStatus, UserRole
from app.models.listing import Listing
from app.models.profile import ApprenantProfile, MentorProfile
from app.models.user import User
from app.schemas.category import CategoryPublic
from app.schemas.listing import ListingPublic
from app.schemas.user import ApprenantSummary, MentorSummary
from app.services.serializers import (
    apprenant_to_summary,
    category_to_public,
    mentor_to_summary,
)

router = APIRouter(prefix="/public", tags=["Public"])


@router.get("/categories", response_model=list[CategoryPublic])
def list_categories(db: DbSession) -> list[CategoryPublic]:
    """Accueil + filtres — grille de catégories."""
    categories = db.scalars(
        select(Category).where(Category.is_active.is_(True)).order_by(Category.sort_order)
    ).all()
    return [category_to_public(c) for c in categories]


@router.get("/mentors", response_model=list[MentorSummary])
def list_mentors(db: DbSession) -> list[MentorSummary]:
    """Page /mentors — annuaire public."""
    rows = db.execute(
        select(User, MentorProfile)
        .join(MentorProfile, MentorProfile.user_id == User.id)
        .where(User.role == UserRole.MENTOR, User.is_active.is_(True))
        .order_by(MentorProfile.score.desc())
    ).all()
    return [mentor_to_summary(user, profile) for user, profile in rows]


@router.get("/mentors/{mentor_id}", response_model=MentorSummary)
def get_mentor(mentor_id: UUID, db: DbSession) -> MentorSummary:
    """Page /mentors/[id]."""
    row = db.execute(
        select(User, MentorProfile)
        .join(MentorProfile, MentorProfile.user_id == User.id)
        .where(User.id == mentor_id, User.role == UserRole.MENTOR)
    ).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentor introuvable")
    user, profile = row
    return mentor_to_summary(user, profile)


@router.get("/apprenants/{apprenant_id}", response_model=ApprenantSummary)
def get_apprenant(apprenant_id: UUID, db: DbSession) -> ApprenantSummary:
    """Page /apprenants/[id] — portfolio public."""
    row = db.execute(
        select(User, ApprenantProfile)
        .join(ApprenantProfile, ApprenantProfile.user_id == User.id)
        .where(User.id == apprenant_id, User.role == UserRole.APPRENANT)
    ).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Apprenant introuvable")
    user, profile = row
    return apprenant_to_summary(user, profile)


@router.get("/listings/{listing_id}", response_model=ListingPublic)
def get_listing(listing_id: UUID, db: DbSession) -> ListingPublic:
    """Page /annonces/[id]."""
    listing = db.get(Listing, listing_id)
    if not listing or listing.status not in (ListingStatus.OPEN, ListingStatus.CLOSED):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Annonce introuvable")
    return listing


@router.get("/listings", response_model=list[ListingPublic])
def list_open_listings(db: DbSession) -> list[ListingPublic]:
    """Page /apprenant/decouvrir — annonces ouvertes."""
    return list(
        db.scalars(
            select(Listing)
            .where(Listing.status == ListingStatus.OPEN)
            .order_by(Listing.created_at.desc())
        ).all()
    )
