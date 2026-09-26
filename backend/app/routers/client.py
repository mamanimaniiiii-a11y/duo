from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select

from app.core.deps import DbSession, require_roles
from app.models.enums import ProjectStatus, UserRole
from app.models.profile import MentorProfile
from app.models.project import Deliverable, Project
from app.models.user import User
from app.schemas.dashboard import DashboardStats
from app.schemas.project import ClientProjectDetail, DeliverablePublic, ProjectCreate, ProjectUpdate
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
        category_id=payload.category_id,
        budget_dzd=payload.budget_dzd,
        deadline=payload.deadline,
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

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
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
    project.status = ProjectStatus.PUBLISHED
    db.commit()
    db.refresh(project)
    return _to_client_project_detail(db, project)


def _to_client_project_detail(db: DbSession, project: Project) -> ClientProjectDetail:
    mentor_summary = None
    if project.mentor_id:
        mentor = db.get(User, project.mentor_id)
        profile = db.scalar(select(MentorProfile).where(MentorProfile.user_id == project.mentor_id))
        if mentor:
            mentor_summary = mentor_to_summary(mentor, profile)

    deliverables = db.scalars(
        select(Deliverable).where(Deliverable.project_id == project.id)
    ).all()

    return ClientProjectDetail(
        id=project.id,
        title=project.title,
        description=project.description,
        category_id=project.category_id,
        status=project.status,
        budget_dzd=project.budget_dzd,
        deadline=project.deadline,
        progress_percent=project.progress_percent,
        mentor=mentor_summary,
        deliverables=[DeliverablePublic.model_validate(d) for d in deliverables],
    )
