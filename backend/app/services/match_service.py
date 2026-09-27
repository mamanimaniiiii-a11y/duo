from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import UserRole
from app.models.profile import MentorProfile
from app.models.project import Project
from app.models.user import User

AUTO_ASSIGN_MIN_SCORE = 40


@dataclass(frozen=True)
class MentorMatchResult:
    mentor_user_id: UUID
    mentor_display_name: str
    mentor_username: str
    mentor_score: int
    skills_overlap: int
    skills_match_percent: int
    match_score: int


def _skill_set(skills: list) -> set[str]:
    return {str(s).strip().casefold() for s in skills if str(s).strip()}


def compute_mentor_match_score(
    required_skills: list[str],
    mentor_skills: list[str],
    mentor_score: int,
    *,
    category_match: bool = False,
) -> tuple[int, int, int]:
    required = _skill_set(required_skills)
    mentor = _skill_set(mentor_skills)
    overlap = len(required & mentor) if required else 0

    if required:
        skills_part = int(100 * overlap / len(required))
    elif category_match:
        skills_part = 60
    else:
        skills_part = 20

    score_part = max(0, min(int(mentor_score), 100))
    category_bonus = 10 if category_match else 0
    # 50 % compétences + 50 % score mentor (le score compte autant que les skills)
    match_score = min(int(skills_part * 0.5 + score_part * 0.5 + category_bonus), 100)
    return match_score, overlap, skills_part


def list_mentor_matches_for_project(db: Session, project: Project) -> list[MentorMatchResult]:
    rows = db.execute(
        select(User, MentorProfile)
        .join(MentorProfile, MentorProfile.user_id == User.id)
        .where(User.role == UserRole.MENTOR, User.is_active.is_(True))
    ).all()

    matches: list[MentorMatchResult] = []
    for user, profile in rows:
        category_ids = {category.id for category in profile.categories}
        match_score, overlap, skills_part = compute_mentor_match_score(
            project.required_skills or [],
            profile.skills or [],
            profile.score,
            category_match=project.category_id in category_ids,
        )
        matches.append(
            MentorMatchResult(
                mentor_user_id=user.id,
                mentor_display_name=user.display_name,
                mentor_username=user.username or "",
                mentor_score=profile.score,
                skills_overlap=overlap,
                skills_match_percent=skills_part,
                match_score=match_score,
            )
        )

    matches.sort(key=lambda item: item.match_score, reverse=True)
    return matches


def find_best_mentor_for_project(db: Session, project: Project) -> MentorMatchResult | None:
    matches = list_mentor_matches_for_project(db, project)
    if not matches:
        return None

    required = _skill_set(project.required_skills or [])
    best = matches[0]
    if best.match_score < AUTO_ASSIGN_MIN_SCORE:
        return None
    if required and best.skills_overlap < 1:
        return None
    return best


def compute_match_for_mentor(
    db: Session,
    project: Project,
    mentor_user: User,
) -> MentorMatchResult | None:
    profile = db.scalar(select(MentorProfile).where(MentorProfile.user_id == mentor_user.id))
    if not profile:
        return None

    category_ids = {category.id for category in profile.categories}
    match_score, overlap, skills_part = compute_mentor_match_score(
        project.required_skills or [],
        profile.skills or [],
        profile.score,
        category_match=project.category_id in category_ids,
    )
    return MentorMatchResult(
        mentor_user_id=mentor_user.id,
        mentor_display_name=mentor_user.display_name,
        mentor_username=mentor_user.username or "",
        mentor_score=profile.score,
        skills_overlap=overlap,
        skills_match_percent=skills_part,
        match_score=match_score,
    )
