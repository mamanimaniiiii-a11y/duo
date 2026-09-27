from dataclasses import dataclass
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.category import Category
from app.models.enums import ListingStatus, Locale, ReviewType, TaskStatus
from app.models.listing import Listing
from app.models.profile import ApprenantProfile
from app.models.project import Project, Task
from app.models.review import Review
from app.models.user import User
from app.schemas.ai import AiGapRecommendation
from app.services.ai.ai_provider import AIProvider
from app.services.ai.prompts import (
    GAP_ANALYSIS_JSON_SCHEMA,
    build_gap_analysis_system_prompt,
    build_gap_analysis_user_prompt,
    resolve_output_locale,
)

HistoryRichness = str  # "empty" | "sparse" | "rich"


@dataclass(frozen=True)
class LearnerGapContext:
    display_name: str
    career_goal: str
    declared_skills: list[str]
    history_richness: HistoryRichness
    missions: list[dict]
    reviews: list[dict]
    touched_categories: list[str]
    opportunities: list[dict]
    allowed_project_ids: frozenset[UUID]


def _task_outcome(task_status: TaskStatus) -> str:
    if task_status == TaskStatus.APPROVED:
        return "succeeded"
    if task_status == TaskStatus.REVISION:
        return "needs_rework"
    if task_status == TaskStatus.SUBMITTED:
        return "pending_review"
    return "in_progress"


def _compute_history_richness(mission_count: int, approved_count: int, review_count: int) -> HistoryRichness:
    if mission_count == 0 and review_count == 0:
        return "empty"
    if approved_count <= 1 and review_count <= 1:
        return "sparse"
    return "rich"


def build_learner_gap_context(db: Session, apprenant: User) -> LearnerGapContext:
    profile = db.scalar(
        select(ApprenantProfile).where(ApprenantProfile.user_id == apprenant.id)
    )
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil apprenant introuvable. Complétez l'onboarding.",
        )

    tasks = db.scalars(
        select(Task)
        .where(Task.assigned_apprenant_id == apprenant.id)
        .order_by(Task.created_at.desc())
    ).all()

    missions: list[dict] = []
    touched_category_slugs: set[str] = set()

    for task in tasks:
        project = db.get(Project, task.project_id)
        category = db.get(Category, project.category_id) if project else None
        if category:
            touched_category_slugs.add(f"{category.name_fr} ({category.slug})")

        missions.append(
            {
                "task_title": task.title,
                "task_status": task.status.value,
                "outcome": _task_outcome(task.status),
                "project_title": project.title if project else "—",
                "project_status": project.status.value if project else "—",
                "category_name": category.name_fr if category else "—",
                "required_skills": list(project.required_skills or []) if project else [],
            }
        )

    reviews_rows = db.scalars(
        select(Review)
        .where(
            Review.to_user_id == apprenant.id,
            Review.type == ReviewType.MENTOR_TO_APPRENANT,
        )
        .order_by(Review.created_at.desc())
    ).all()
    reviews = [
        {
            "rating": row.rating,
            "comment": row.comment,
            "project_id": str(row.project_id) if row.project_id else None,
        }
        for row in reviews_rows
    ]

    approved_count = sum(1 for task in tasks if task.status == TaskStatus.APPROVED)
    history_richness = _compute_history_richness(len(tasks), approved_count, len(reviews))

    listings = db.scalars(
        select(Listing)
        .where(
            Listing.status == ListingStatus.OPEN,
            Listing.project_id.is_not(None),
        )
        .order_by(Listing.created_at.desc())
        .limit(20)
    ).all()

    opportunities: list[dict] = []
    allowed_ids: set[UUID] = set()

    for listing in listings:
        if not listing.project_id:
            continue
        project = db.get(Project, listing.project_id)
        if not project:
            continue
        category = db.get(Category, project.category_id)
        allowed_ids.add(project.id)
        opportunities.append(
            {
                "project_id": str(project.id),
                "project_title": project.title,
                "category_name": category.name_fr if category else "—",
                "learner_complexity_level": project.learner_complexity_level.value,
                "project_required_skills": list(project.required_skills or []),
                "listing_title": listing.title,
                "listing_required_skills": list(listing.required_skills or []),
            }
        )

    return LearnerGapContext(
        display_name=apprenant.display_name,
        career_goal=profile.career_goal or "",
        declared_skills=list(profile.skills or []),
        history_richness=history_richness,
        missions=missions,
        reviews=reviews,
        touched_categories=sorted(touched_category_slugs),
        opportunities=opportunities,
        allowed_project_ids=frozenset(allowed_ids),
    )


def _normalize_gap_response(raw: dict) -> dict:
    skill_gap = raw.get("skill_gap")
    if isinstance(skill_gap, list):
        raw["skill_gap"] = "\n".join(
            f"- {item}" if not str(item).lstrip().startswith("-") else str(item)
            for item in skill_gap
        )
    explanation = raw.get("explanation")
    if isinstance(explanation, list):
        raw["explanation"] = " ".join(str(item) for item in explanation)
    ideas = raw.get("suggested_project_ideas")
    if ideas is None:
        raw["suggested_project_ideas"] = []
    elif isinstance(ideas, list):
        normalized_ideas: list[dict] = []
        for idea in ideas[:3]:
            if not isinstance(idea, dict):
                continue
            skills = idea.get("target_skills") or []
            if isinstance(skills, str):
                skills = [part.strip() for part in skills.replace("،", ",").split(",") if part.strip()]
            elif isinstance(skills, list):
                skills = [str(skill) for skill in skills[:6] if str(skill).strip()]
            else:
                skills = []
            normalized_ideas.append(
                {
                    "title": str(idea.get("title", "")),
                    "description": str(idea.get("description", "")),
                    "target_skills": skills,
                }
            )
        raw["suggested_project_ideas"] = normalized_ideas
    return raw


def _apply_gap_recommendation_guardrails(
    recommendation: AiGapRecommendation,
    allowed_project_ids: frozenset[UUID],
) -> AiGapRecommendation:
    filtered_ids = _filter_recommended_project_ids(
        [str(pid) for pid in recommendation.recommended_project_ids],
        allowed_project_ids,
    )
    catalog_has_opportunities = bool(allowed_project_ids)
    if filtered_ids or catalog_has_opportunities:
        ideas = []
    else:
        ideas = recommendation.suggested_project_ideas[:3]
    return AiGapRecommendation(
        skill_gap=recommendation.skill_gap,
        recommended_project_ids=filtered_ids,
        explanation=recommendation.explanation,
        suggested_project_ideas=ideas,
    )


def _filter_recommended_project_ids(
    raw_ids: list,
    allowed: frozenset[UUID],
) -> list[UUID]:
    filtered: list[UUID] = []
    seen: set[UUID] = set()
    for raw in raw_ids:
        try:
            project_id = UUID(str(raw))
        except (TypeError, ValueError):
            continue
        if project_id not in allowed or project_id in seen:
            continue
        seen.add(project_id)
        filtered.append(project_id)
    return filtered[:5]


def generate_gap_analysis(db: Session, apprenant: User) -> AiGapRecommendation:
    settings = get_settings()
    if not settings.ai_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Les fonctionnalités IA sont désactivées",
        )

    context = build_learner_gap_context(db, apprenant)
    locale = resolve_output_locale(
        apprenant.locale.value if apprenant.locale else Locale.FR.value
    )
    system_prompt = build_gap_analysis_system_prompt(locale)
    user_prompt = build_gap_analysis_user_prompt(
        locale=locale,
        display_name=context.display_name,
        career_goal=context.career_goal,
        declared_skills=context.declared_skills,
        history_richness=context.history_richness,
        missions=context.missions,
        reviews=context.reviews,
        touched_categories=context.touched_categories,
        opportunities=context.opportunities,
    )

    try:
        client = AIProvider()
        raw = client.complete_json_schema(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema_name="gap_analysis",
            schema=GAP_ANALYSIS_JSON_SCHEMA,
        )
        recommendation = AiGapRecommendation.model_validate(_normalize_gap_response(raw))
        return _apply_gap_recommendation_guardrails(recommendation, context.allowed_project_ids)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Échec de l'analyse de lacunes IA : {exc}",
        ) from exc
