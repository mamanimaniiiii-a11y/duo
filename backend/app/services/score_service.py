from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.enums import ProjectStatus, ReviewType, UserRole
from app.models.profile import ApprenantProfile, MentorProfile
from app.models.project import Project
from app.models.review import Review
from app.models.user import User
from app.schemas.common import ScoreBreakdown


def _clamp_score(value: float) -> int:
    return max(0, min(100, int(round(value))))


def compute_mentor_score_breakdown(db: Session, user: User) -> ScoreBreakdown:
    profile = db.scalar(select(MentorProfile).where(MentorProfile.user_id == user.id))
    if not profile:
        return ScoreBreakdown(total=0)

    avg_rating = db.scalar(
        select(func.avg(Review.rating)).where(
            Review.to_user_id == user.id,
            Review.type.in_(
                [ReviewType.CLIENT_TO_MENTOR, ReviewType.APPRENANT_TO_MENTOR]
            ),
        )
    ) or 0.0

    projects_completed = profile.projects_completed_count or db.scalar(
        select(func.count(Project.id)).where(
            Project.mentor_id == user.id,
            Project.status == ProjectStatus.COMPLETED,
        )
    ) or 0

    apprentices = profile.apprentices_mentored_count

    # Score 0-100 : projets (40%), apprentis (30%), note moyenne (30%)
    project_part = min(projects_completed * 8, 40)
    apprentice_part = min(apprentices * 5, 30)
    rating_part = (avg_rating / 5) * 30
    total = _clamp_score(project_part + apprentice_part + rating_part)

    profile.score = total
    profile.average_rating = float(avg_rating)
    profile.projects_completed_count = projects_completed
    db.commit()

    return ScoreBreakdown(
        total=total,
        projects_completed=projects_completed,
        apprentices_mentored=apprentices,
        average_rating=float(avg_rating),
    )


def compute_apprenant_score_breakdown(db: Session, user: User) -> ScoreBreakdown:
    profile = db.scalar(select(ApprenantProfile).where(ApprenantProfile.user_id == user.id))
    if not profile:
        return ScoreBreakdown(total=0)

    avg_rating = db.scalar(
        select(func.avg(Review.rating)).where(
            Review.to_user_id == user.id,
            Review.type == ReviewType.MENTOR_TO_APPRENANT,
        )
    ) or 0.0

    projects_completed = profile.projects_completed_count or 0
    project_part = min(projects_completed * 12, 60)
    rating_part = (avg_rating / 5) * 40
    total = _clamp_score(project_part + rating_part)

    profile.score = total
    profile.average_rating = float(avg_rating)
    profile.can_become_freelance = total >= 70
    db.commit()

    return ScoreBreakdown(
        total=total,
        projects_completed=projects_completed,
        average_rating=float(avg_rating),
    )


def refresh_mentor_score_after_project_completed(db: Session, user: User) -> ScoreBreakdown:
    """
    Recalcule le score mentor après complétion d'un projet.
    Le compteur « projets réalisés » ne compte que status=completed (pas à la prise en charge).
    """
    return compute_mentor_score_breakdown(db, user)


def get_score_breakdown_for_user(db: Session, user: User) -> ScoreBreakdown | None:
    if user.role == UserRole.MENTOR:
        return compute_mentor_score_breakdown(db, user)
    if user.role == UserRole.APPRENANT:
        return compute_apprenant_score_breakdown(db, user)
    return None
