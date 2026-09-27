from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.enums import ProjectStatus, ReviewType, TaskStatus, UserRole
from app.models.profile import ApprenantProfile, MentorProfile
from app.models.project import Project, Task
from app.models.review import Review
from app.models.user import User
from app.schemas.common import ScoreBreakdown
from app.services.mentor_score import calculate_mentor_score


def _fetch_mentor_score_inputs(
    db: Session, mentor_user_id: UUID
) -> tuple[int, int, list[int], list[int]]:
    projects_completed = db.scalar(
        select(func.count(Project.id)).where(
            Project.mentor_id == mentor_user_id,
            Project.status == ProjectStatus.COMPLETED,
        )
    ) or 0

    apprentice_ids = db.scalars(
        select(Task.assigned_apprenant_id)
        .join(Project, Project.id == Task.project_id)
        .where(
            Project.mentor_id == mentor_user_id,
            Task.status == TaskStatus.APPROVED,
            Task.assigned_apprenant_id.is_not(None),
        )
        .distinct()
    ).all()
    apprentices_mentored = len(apprentice_ids)

    client_reviews = list(
        db.scalars(
            select(Review.rating).where(
                Review.to_user_id == mentor_user_id,
                Review.type == ReviewType.CLIENT_TO_MENTOR,
            )
        ).all()
    )
    apprentice_reviews = list(
        db.scalars(
            select(Review.rating).where(
                Review.to_user_id == mentor_user_id,
                Review.type == ReviewType.APPRENANT_TO_MENTOR,
            )
        ).all()
    )
    return projects_completed, apprentices_mentored, client_reviews, apprentice_reviews


def recalculate_mentor_score(db: Session, user: User) -> ScoreBreakdown:
    """Recalcule et persiste mentor_profiles.score (formule §5bis.2)."""
    profile = db.scalar(select(MentorProfile).where(MentorProfile.user_id == user.id))
    if not profile:
        return ScoreBreakdown(total=0)

    projects_completed, apprentices_mentored, client_reviews, apprentice_reviews = (
        _fetch_mentor_score_inputs(db, user.id)
    )
    total = calculate_mentor_score(
        projects_completed,
        apprentices_mentored,
        client_reviews,
        apprentice_reviews,
    )

    all_ratings = client_reviews + apprentice_reviews
    average_rating = sum(all_ratings) / len(all_ratings) if all_ratings else 0.0

    profile.score = total
    profile.average_rating = float(average_rating)
    profile.projects_completed_count = projects_completed
    profile.apprentices_mentored_count = apprentices_mentored
    db.commit()

    return ScoreBreakdown(
        total=total,
        projects_completed=projects_completed,
        apprentices_mentored=apprentices_mentored,
        average_rating=float(average_rating),
    )


def compute_mentor_score_breakdown(db: Session, user: User) -> ScoreBreakdown:
    return recalculate_mentor_score(db, user)


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
    total = max(0, min(100, int(round(project_part + rating_part))))

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
    """Recalcule le score mentor après complétion d'un projet."""
    return recalculate_mentor_score(db, user)


def get_score_breakdown_for_user(db: Session, user: User) -> ScoreBreakdown | None:
    if user.role == UserRole.MENTOR:
        return recalculate_mentor_score(db, user)
    if user.role == UserRole.APPRENANT:
        return compute_apprenant_score_breakdown(db, user)
    return None
