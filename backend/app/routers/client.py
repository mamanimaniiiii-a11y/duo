from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select

from app.core.deps import DbSession, require_roles
from app.models.enums import ProjectStatus, UserRole
from app.models.profile import MentorProfile
from app.models.project import Deliverable, Project
from app.models.user import User
from app.schemas.dashboard import DashboardStats
from app.schemas.project import (
    AssignMentorRequest,
    ClientProjectDetail,
    DeliverablePublic,
    MentorMatchPublic,
    ProjectCreate,
    ProjectUpdate,
)
from app.services.match_service import (
    compute_match_for_mentor,
    list_mentor_matches_for_project,
)
from app.services.notification_service import create_notification
from app.services.score_service import recalculate_mentor_score
from app.services.serializers import mentor_to_summary

router = APIRouter(
    prefix="/client",
    tags=["Client"],
    dependencies=[Depends(require_roles(UserRole.CLIENT))],
)


@router.get("/dashboard", response_model=DashboardStats)
def client_dashboard(db: DbSession, current_user: User = Depends(require_roles(UserRole.CLIENT))) -> DashboardStats:
    """Page /client/dashboard."""
    active = db.scalar(
        select(func.count(Project.id)).where(
            Project.client_id == current_user.id,
            Project.status.in_(
                [ProjectStatus.PUBLISHED, ProjectStatus.ASSIGNED, ProjectStatus.IN_PROGRESS]
            ),
        )
    ) or 0
    completed = db.scalar(
        select(func.count(Project.id)).where(
            Project.client_id == current_user.id,
            Project.status == ProjectStatus.COMPLETED,
        )
    ) or 0
    return DashboardStats(active_projects=active, completed_projects=completed)


@router.get("/projects", response_model=list[ClientProjectDetail])
def list_client_projects(
    db: DbSession, current_user: User = Depends(require_roles(UserRole.CLIENT))
) -> list[ClientProjectDetail]:
    """Page /client/projets."""
    projects = db.scalars(
        select(Project).where(Project.client_id == current_user.id).order_by(Project.created_at.desc())
    ).all()
    return [_to_client_project_detail(db, p) for p in projects]


@router.post("/projects", response_model=ClientProjectDetail, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.CLIENT)),
) -> ClientProjectDetail:
    """Page /client/projets/nouveau."""
    project = Project(
        client_id=current_user.id,
        title=payload.title,
        description=payload.description,
        description_format=payload.description_format,
        learner_complexity_level=payload.learner_complexity_level,
        category_id=payload.category_id,
        budget_dzd=payload.budget_dzd,
        deadline=payload.deadline,
        required_skills=payload.required_skills,
        status=ProjectStatus.DRAFT,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return _to_client_project_detail(db, project)


@router.get("/projects/{project_id}", response_model=ClientProjectDetail)
def get_client_project(
    project_id: UUID,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.CLIENT)),
) -> ClientProjectDetail:
    """Page /client/projets/[id]."""
    project = db.get(Project, project_id)
    if not project or project.client_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable")
    return _to_client_project_detail(db, project)


@router.patch("/projects/{project_id}", response_model=ClientProjectDetail)
def update_client_project(
    project_id: UUID,
    payload: ProjectUpdate,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.CLIENT)),
) -> ClientProjectDetail:
    project = db.get(Project, project_id)
    if not project or project.client_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable")

    previous_status = project.status
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    if (
        project.status == ProjectStatus.COMPLETED
        and previous_status != ProjectStatus.COMPLETED
        and project.mentor_id is not None
    ):
        mentor = db.get(User, project.mentor_id)
        if mentor:
            recalculate_mentor_score(db, mentor)
    return _to_client_project_detail(db, project)


@router.post("/projects/{project_id}/publish", response_model=ClientProjectDetail)
def publish_project(
    project_id: UUID,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.CLIENT)),
) -> ClientProjectDetail:
    project = db.get(Project, project_id)
    if not project or project.client_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable")
    if project.status != ProjectStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Seuls les projets en brouillon peuvent être publiés",
        )
    project.status = ProjectStatus.PUBLISHED
    db.commit()
    db.refresh(project)
    return _to_client_project_detail(db, project)


@router.get("/projects/{project_id}/mentor-matches", response_model=list[MentorMatchPublic])
def list_project_mentor_matches(
    project_id: UUID,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.CLIENT)),
) -> list[MentorMatchPublic]:
    project = db.get(Project, project_id)
    if not project or project.client_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable")

    results: list[MentorMatchPublic] = []
    for match in list_mentor_matches_for_project(db, project):
        mentor = db.get(User, match.mentor_user_id)
        profile = db.scalar(select(MentorProfile).where(MentorProfile.user_id == match.mentor_user_id))
        if not mentor:
            continue
        results.append(
            MentorMatchPublic(
                mentor=mentor_to_summary(mentor, profile),
                match_score=match.match_score,
                skills_overlap=match.skills_overlap,
                skills_match_percent=match.skills_match_percent,
                mentor_score=match.mentor_score,
            )
        )
    return results


@router.post("/projects/{project_id}/assign-mentor", response_model=ClientProjectDetail)
def assign_project_mentor(
    project_id: UUID,
    payload: AssignMentorRequest,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.CLIENT)),
) -> ClientProjectDetail:
    project = db.get(Project, project_id)
    if not project or project.client_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable")
    if project.status != ProjectStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Seuls les projets publiés sans mentor peuvent recevoir une assignation",
        )
    if project.mentor_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce projet a déjà un mentor assigné",
        )

    mentor = db.get(User, payload.mentor_id)
    if not mentor or mentor.role != UserRole.MENTOR or not mentor.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mentor invalide")

    match = compute_match_for_mentor(db, project, mentor)
    project.mentor_id = mentor.id
    project.status = ProjectStatus.ASSIGNED

    match_score = match.match_score if match else 0
    create_notification(
        db,
        user_id=mentor.id,
        title="Projet assigné par le client",
        body=(
            f"{current_user.display_name} vous a choisi pour le projet « {project.title} » "
            f"(compatibilité {match_score}%)."
        ),
        link=f"/mentor/projets/{project.id}",
        extra_data={
            "type": "project_assigned_by_client",
            "project_id": str(project.id),
            "match_score": match_score,
        },
    )
    create_notification(
        db,
        user_id=current_user.id,
        title="Mentor choisi",
        body=(
            f"Vous avez assigné {mentor.display_name} (@{mentor.username}) "
            f"au projet « {project.title} » (compatibilité {match_score}%)."
        ),
        link=f"/client/projets/{project.id}",
        extra_data={
            "type": "mentor_chosen",
            "project_id": str(project.id),
            "mentor_id": str(mentor.id),
        },
    )

    db.commit()
    db.refresh(project)
    return _to_client_project_detail(db, project)


def _to_client_project_detail(db: DbSession, project: Project) -> ClientProjectDetail:
    mentor_summary = None
    mentor_match_score = None
    if project.mentor_id:
        mentor = db.get(User, project.mentor_id)
        profile = db.scalar(select(MentorProfile).where(MentorProfile.user_id == project.mentor_id))
        if mentor:
            mentor_summary = mentor_to_summary(mentor, profile)
            match = compute_match_for_mentor(db, project, mentor)
            if match:
                mentor_match_score = match.match_score

    deliverables = db.scalars(
        select(Deliverable).where(Deliverable.project_id == project.id)
    ).all()

    return ClientProjectDetail(
        id=project.id,
        title=project.title,
        description=project.description,
        description_format=project.description_format,
        learner_complexity_level=project.learner_complexity_level,
        category_id=project.category_id,
        status=project.status,
        budget_dzd=project.budget_dzd,
        deadline=project.deadline,
        progress_percent=project.progress_percent,
        required_skills=project.required_skills or [],
        mentor_match_score=mentor_match_score,
        mentor=mentor_summary,
        deliverables=[DeliverablePublic.model_validate(d) for d in deliverables],
    )
