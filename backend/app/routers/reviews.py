from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.deps import CurrentUser, DbSession
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewPublic
from app.services.score_service import get_score_breakdown_for_user

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("", response_model=ReviewPublic, status_code=status.HTTP_201_CREATED)
def create_review(
    payload: ReviewCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> ReviewPublic:
    """Avis après projet — alimente le score mentor/apprenant."""
    review = Review(
        from_user_id=current_user.id,
        to_user_id=payload.to_user_id,
        project_id=payload.project_id,
        rating=payload.rating,
        comment=payload.comment,
        type=payload.type,
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    from app.models.user import User

    to_user = db.get(User, payload.to_user_id)
    if to_user:
        get_score_breakdown_for_user(db, to_user)

    return review


@router.get("/user/{user_id}", response_model=list[ReviewPublic])
def list_reviews_for_user(user_id: UUID, db: DbSession) -> list[ReviewPublic]:
    """Profils publics / progression."""
    return list(
        db.scalars(
            select(Review).where(Review.to_user_id == user_id).order_by(Review.created_at.desc())
        ).all()
    )
