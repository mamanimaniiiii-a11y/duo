from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select

from app.core.deps import DbSession, require_roles
from app.models.application import Application
from app.models.boost import BoostOption, BoostSubscription, PremiumPlan, PremiumSubscription
from app.models.enums import (
    ApplicationStatus,
    ListingStatus,
    ProjectStatus,
    SubscriptionStatus,
    UserRole,
)
from app.models.listing import Listing
from app.models.pack import MentorPack
from app.models.profile import ApprenantProfile, MentorProfile
from app.models.project import Deliverable, Project, Task
from app.models.user import User
from app.schemas.boost import BoostOptionPublic, BoostSubscribeRequest, PremiumPlanPublic, PremiumSubscribeRequest, SubscriptionPublic
from app.schemas.common import LocalizedString, MessageResponse, ScoreBreakdown
from app.schemas.dashboard import DashboardStats
from app.schemas.listing import ApplicationPublic, ApplicationUpdate, ListingCreate, ListingPublic, ListingUpdate
from app.schemas.pack import MentorPackCreate, MentorPackPublic, MentorPackUpdate
from app.schemas.project import (
    AvailableProjectPublic,
    DeliverablePublic,
    MentorProjectDetail,
    TaskCreate,
    TaskPublic,
    TaskUpdate,
)
from app.schemas.user import ApprenantSummary, UserSummary
from app.services.score_service import compute_mentor_score_breakdown
from app.services.serializers import apprenant_to_summary, user_to_summary


def _require_mentor_project(db: DbSession, project_id: UUID, mentor_id: UUID) -> Project:
    project = db.get(Project, project_id)
    if not project or project.mentor_id != mentor_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable")
    return project


def _validate_pack_project(db: DbSession, project_id: UUID | None, mentor_id: UUID) -> None:
    if project_id is not None:
        _require_mentor_project(db, project_id, mentor_id)

router = APIRouter(
    prefix="/mentor",
    tags=["Mentor"],
    dependencies=[Depends(require_roles(UserRole.MENTOR))],
)


@router.get("/dashboard", response_model=DashboardStats)
def mentor_dashboard(
    db: DbSession, current_user: User = Depends(require_roles(UserRole.MENTOR))
) -> DashboardStats:
    """Page /mentor/dashboard."""
    active = db.scalar(
        select(func.count(Project.id)).where(
            Project.mentor_id == current_user.id,
            Project.status.in_([ProjectStatus.ASSIGNED, ProjectStatus.IN_PROGRESS]),
        )
    ) or 0
    open_listings = db.scalar(
        select(func.count(Listing.id)).where(
            Listing.mentor_id == current_user.id,
            Listing.status == ListingStatus.OPEN,
        )
    ) or 0
    pending_apps = db.scalar(
        select(func.count(Application.id))
        .join(Listing, Listing.id == Application.listing_id)
        .where(Listing.mentor_id == current_user.id, Application.status == ApplicationStatus.PENDING)
    ) or 0
    score = compute_mentor_score_breakdown(db, current_user)
    return DashboardStats(
        active_projects=active,
        open_listings=open_listings,
        pending_applications=pending_apps,
        score_breakdown=score,
    )


@router.get("/projects", response_model=list[MentorProjectDetail])
def list_mentor_projects(
    db: DbSession, current_user: User = Depends(require_roles(UserRole.MENTOR))
) -> list[MentorProjectDetail]:
    """Page /mentor/projets."""
    projects = db.scalars(
        select(Project).where(Project.mentor_id == current_user.id).order_by(Project.created_at.desc())
    ).all()
    return [_to_mentor_project_detail(db, p) for p in projects]


@router.get("/projects/disponibles", response_model=list[AvailableProjectPublic])
def list_available_projects(
    db: DbSession, current_user: User = Depends(require_roles(UserRole.MENTOR))
) -> list[AvailableProjectPublic]:
    """Projets publiés par des clients, sans mentor assigné."""
    projects = db.scalars(
        select(Project)
        .where(
            Project.status == ProjectStatus.PUBLISHED,
            Project.mentor_id.is_(None),
        )
        .order_by(Project.created_at.desc())
    ).all()
    return [_to_available_project(db, p) for p in projects]


@router.post(
    "/projects/{project_id}/prendre-en-charge",
    response_model=MentorProjectDetail,
    status_code=status.HTTP_200_OK,
)
def claim_project(
    project_id: UUID,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.MENTOR)),
) -> MentorProjectDetail:
    """Assigne le projet au mentor connecté et passe le statut à assigned."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable")
    if project.status != ProjectStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce projet n'est pas disponible pour prise en charge",
        )
    if project.mentor_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce projet a déjà un mentor assigné",
        )

    project.mentor_id = current_user.id
    project.status = ProjectStatus.ASSIGNED
    db.commit()
    db.refresh(project)
    return _to_mentor_project_detail(db, project)


@router.get("/projects/{project_id}", response_model=MentorProjectDetail)
def get_mentor_project(
    project_id: UUID,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.MENTOR)),
) -> MentorProjectDetail:
    """Page /mentor/projets/[id]."""
    project = db.get(Project, project_id)
    if not project or project.mentor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable")
    return _to_mentor_project_detail(db, project)


@router.get("/projects/{project_id}/eligible-apprenants", response_model=list[ApprenantSummary])
def list_eligible_apprenants(
    project_id: UUID,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.MENTOR)),
) -> list[ApprenantSummary]:
    """Apprenants acceptés sur les annonces du projet."""
    _require_mentor_project(db, project_id, current_user.id)
    listing_ids = db.scalars(
        select(Listing.id).where(
            Listing.project_id == project_id,
            Listing.mentor_id == current_user.id,
        )
    ).all()
    apprenant_ids: set[UUID] = set()
    if listing_ids:
        for aid in db.scalars(
            select(Application.apprenant_id).where(
                Application.listing_id.in_(listing_ids),
                Application.status == ApplicationStatus.ACCEPTED,
            )
        ).all():
            if aid:
                apprenant_ids.add(aid)
    for aid in db.scalars(
        select(Task.assigned_apprenant_id).where(
            Task.project_id == project_id,
            Task.assigned_apprenant_id.is_not(None),
        )
    ).all():
        if aid:
            apprenant_ids.add(aid)
    results: list[ApprenantSummary] = []
    for aid in apprenant_ids:
        user = db.get(User, aid)
        profile = db.scalar(select(ApprenantProfile).where(ApprenantProfile.user_id == aid))
        if user and user.role == UserRole.APPRENANT:
            results.append(apprenant_to_summary(user, profile))
    return results


@router.post(
    "/projects/{project_id}/tasks",
    response_model=TaskPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_project_task(
    project_id: UUID,
    payload: TaskCreate,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.MENTOR)),
) -> TaskPublic:
    project = _require_mentor_project(db, project_id, current_user.id)
    max_order = db.scalar(
        select(func.coalesce(func.max(Task.sort_order), -1)).where(Task.project_id == project.id)
    )
    sort_order = payload.sort_order if payload.sort_order is not None else (max_order or 0) + 1
    task = Task(
        project_id=project.id,
        title=payload.title,
        description=payload.description,
        acceptance_criteria=payload.acceptance_criteria,
        due_date=payload.due_date,
        sort_order=sort_order,
    )
    db.add(task)
    if project.status == ProjectStatus.ASSIGNED:
        project.status = ProjectStatus.IN_PROGRESS
    db.commit()
    db.refresh(task)
    return TaskPublic.model_validate(task)


@router.patch("/projects/{project_id}/tasks/{task_id}", response_model=TaskPublic)
def update_project_task(
    project_id: UUID,
    task_id: UUID,
    payload: TaskUpdate,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.MENTOR)),
) -> TaskPublic:
    _require_mentor_project(db, project_id, current_user.id)
    task = db.get(Task, task_id)
    if not task or task.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tâche introuvable")
    data = payload.model_dump(exclude_unset=True)
    if "assigned_apprenant_id" in data and data["assigned_apprenant_id"] is not None:
        apprenant = db.get(User, data["assigned_apprenant_id"])
        if not apprenant or apprenant.role != UserRole.APPRENANT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Apprenant invalide",
            )
    for field, value in data.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return TaskPublic.model_validate(task)


@router.get("/projects/{project_id}/packs", response_model=list[MentorPackPublic])
def list_project_packs(
    project_id: UUID,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.MENTOR)),
) -> list[MentorPackPublic]:
    _require_mentor_project(db, project_id, current_user.id)
    return list(
        db.scalars(
            select(MentorPack).where(
                MentorPack.mentor_id == current_user.id,
                MentorPack.project_id == project_id,
            )
        ).all()
    )


@router.get("/recrutement/listings", response_model=list[ListingPublic])
def list_my_listings(
    db: DbSession, current_user: User = Depends(require_roles(UserRole.MENTOR))
) -> list[ListingPublic]:
    """Page /mentor/recrutement."""
    return list(
        db.scalars(
            select(Listing)
            .where(Listing.mentor_id == current_user.id)
            .order_by(Listing.created_at.desc())
        ).all()
    )


@router.post("/recrutement/listings", response_model=ListingPublic, status_code=status.HTTP_201_CREATED)
def create_listing(
    payload: ListingCreate,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.MENTOR)),
) -> ListingPublic:
    listing = Listing(
        mentor_id=current_user.id,
        title=payload.title,
        description=payload.description,
        required_skills=payload.required_skills,
        project_id=payload.project_id,
        status=ListingStatus.DRAFT,
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


@router.patch("/recrutement/listings/{listing_id}", response_model=ListingPublic)
def update_listing(
    listing_id: UUID,
    payload: ListingUpdate,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.MENTOR)),
) -> ListingPublic:
    listing = db.get(Listing, listing_id)
    if not listing or listing.mentor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Annonce introuvable")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(listing, field, value)
    db.commit()
    db.refresh(listing)
    return listing


@router.get("/recrutement/listings/{listing_id}/applications", response_model=list[ApplicationPublic])
def list_listing_applications(
    listing_id: UUID,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.MENTOR)),
) -> list[ApplicationPublic]:
    listing = db.get(Listing, listing_id)
    if not listing or listing.mentor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Annonce introuvable")
    return list(
        db.scalars(select(Application).where(Application.listing_id == listing_id)).all()
    )


@router.patch("/recrutement/applications/{application_id}", response_model=ApplicationPublic)
def update_application_status(
    application_id: UUID,
    payload: ApplicationUpdate,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.MENTOR)),
) -> ApplicationPublic:
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidature introuvable")
    listing = db.get(Listing, application.listing_id)
    if not listing or listing.mentor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès refusé")
    application.status = payload.status
    db.commit()
    db.refresh(application)
    return application


@router.get("/apprenants", response_model=list[dict])
def list_my_apprenants(
    db: DbSession, current_user: User = Depends(require_roles(UserRole.MENTOR))
) -> list[dict]:
    """Page /mentor/apprenants — apprenants assignés via tâches."""
    apprenant_ids = db.scalars(
        select(Task.assigned_apprenant_id)
        .join(Project, Project.id == Task.project_id)
        .where(Project.mentor_id == current_user.id, Task.assigned_apprenant_id.is_not(None))
        .distinct()
    ).all()
    results = []
    for aid in apprenant_ids:
        if not aid:
            continue
        user = db.get(User, aid)
        profile = db.scalar(select(ApprenantProfile).where(ApprenantProfile.user_id == aid))
        if user:
            results.append(apprenant_to_summary(user, profile).model_dump())
    return results


@router.get("/packs", response_model=list[MentorPackPublic])
def list_my_packs(
    db: DbSession, current_user: User = Depends(require_roles(UserRole.MENTOR))
) -> list[MentorPackPublic]:
    """Page /mentor/packs."""
    return list(
        db.scalars(select(MentorPack).where(MentorPack.mentor_id == current_user.id)).all()
    )


@router.post("/packs", response_model=MentorPackPublic, status_code=status.HTTP_201_CREATED)
def create_pack(
    payload: MentorPackCreate,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.MENTOR)),
) -> MentorPackPublic:
    _validate_pack_project(db, payload.project_id, current_user.id)
    pack = MentorPack(mentor_id=current_user.id, **payload.model_dump())
    db.add(pack)
    db.commit()
    db.refresh(pack)
    return pack


@router.patch("/packs/{pack_id}", response_model=MentorPackPublic)
def update_pack(
    pack_id: UUID,
    payload: MentorPackUpdate,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.MENTOR)),
) -> MentorPackPublic:
    pack = db.get(MentorPack, pack_id)
    if not pack or pack.mentor_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pack introuvable")
    data = payload.model_dump(exclude_unset=True)
    if "project_id" in data:
        _validate_pack_project(db, data["project_id"], current_user.id)
    for field, value in data.items():
        setattr(pack, field, value)
    db.commit()
    db.refresh(pack)
    return pack


@router.get("/boost/options", response_model=list[BoostOptionPublic])
def list_boost_options(db: DbSession) -> list[BoostOptionPublic]:
    """Page /mentor/boost — options disponibles."""
    options = db.scalars(select(BoostOption).where(BoostOption.is_active.is_(True))).all()
    return [
        BoostOptionPublic(
            id=o.id,
            label=LocalizedString(fr=o.label_fr, en=o.label_en, ar=o.label_ar),
            duration_days=o.duration_days,
            price_dzd=o.price_dzd,
            is_active=o.is_active,
        )
        for o in options
    ]


@router.post("/boost/subscribe", response_model=SubscriptionPublic, status_code=status.HTTP_201_CREATED)
def subscribe_boost(
    payload: BoostSubscribeRequest,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.MENTOR)),
) -> SubscriptionPublic:
    option = db.get(BoostOption, payload.boost_option_id)
    if not option or not option.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Option boost introuvable")
    sub = BoostSubscription(
        mentor_id=current_user.id,
        boost_option_id=option.id,
        status=SubscriptionStatus.PENDING_PAYMENT,
        amount_dzd=option.price_dzd,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


@router.post("/premium/subscribe", response_model=SubscriptionPublic, status_code=status.HTTP_201_CREATED)
def subscribe_premium(
    payload: PremiumSubscribeRequest,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.MENTOR)),
) -> SubscriptionPublic:
    plan = db.get(PremiumPlan, payload.plan_id)
    if not plan or not plan.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan premium introuvable")
    sub = PremiumSubscription(
        mentor_id=current_user.id,
        plan_id=plan.id,
        status=SubscriptionStatus.PENDING_PAYMENT,
        amount_dzd=plan.price_dzd,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


@router.get("/progression", response_model=ScoreBreakdown)
def mentor_progression(
    db: DbSession, current_user: User = Depends(require_roles(UserRole.MENTOR))
) -> ScoreBreakdown:
    """Page /mentor/progression."""
    return compute_mentor_score_breakdown(db, current_user)


def _to_available_project(db: DbSession, project: Project) -> AvailableProjectPublic:
    client = db.get(User, project.client_id)
    return AvailableProjectPublic(
        id=project.id,
        title=project.title,
        description=project.description,
        category_id=project.category_id,
        status=project.status,
        budget_dzd=project.budget_dzd,
        deadline=project.deadline,
        client=user_to_summary(client)
        if client
        else UserSummary(id=project.client_id, display_name="—"),
    )


def _to_mentor_project_detail(db: DbSession, project: Project) -> MentorProjectDetail:
    client = db.get(User, project.client_id)
    tasks = db.scalars(
        select(Task).where(Task.project_id == project.id).order_by(Task.sort_order)
    ).all()
    deliverables = db.scalars(select(Deliverable).where(Deliverable.project_id == project.id)).all()

    apprenant_ids = {t.assigned_apprenant_id for t in tasks if t.assigned_apprenant_id}
    assigned = []
    for aid in apprenant_ids:
        user = db.get(User, aid)
        profile = db.scalar(select(ApprenantProfile).where(ApprenantProfile.user_id == aid))
        if user:
            assigned.append(apprenant_to_summary(user, profile))

    return MentorProjectDetail(
        id=project.id,
        title=project.title,
        description=project.description,
        category_id=project.category_id,
        status=project.status,
        client=user_to_summary(client)
        if client
        else UserSummary(id=project.client_id, display_name="—"),
        progress_percent=project.progress_percent,
        tasks=[TaskPublic.model_validate(t) for t in tasks],
        deliverables=[DeliverablePublic.model_validate(d) for d in deliverables],
        assigned_apprenants=assigned,
    )
