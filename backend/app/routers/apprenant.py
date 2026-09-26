from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select

from app.core.deps import DbSession, require_roles
from app.models.application import Application
from app.models.enums import ApplicationStatus, PackPurchaseStatus, UserRole
from app.models.listing import Listing
from app.models.pack import MentorPack, PackPurchase
from app.models.project import Deliverable, Project, Submission, Task
from app.models.user import User
from app.schemas.common import ScoreBreakdown
from app.schemas.dashboard import DashboardStats
from app.schemas.listing import ApplicationCreate, ApplicationPublic, ListingPublic
from app.schemas.pack import MentorPackPublic, PackPurchaseCreate, PackPurchasePublic
from app.schemas.project import ApprenantMissionDetail, SubmissionPublic, TaskPublic
from app.services.score_service import compute_apprenant_score_breakdown

router = APIRouter(
    prefix="/apprenant",
    tags=["Apprenant"],
    dependencies=[Depends(require_roles(UserRole.APPRENANT))],
)


@router.get("/dashboard", response_model=DashboardStats)
def apprenant_dashboard(
    db: DbSession, current_user: User = Depends(require_roles(UserRole.APPRENANT))
) -> DashboardStats:
    """Page /apprenant/dashboard."""
    active_missions = db.scalar(
        select(func.count(Task.id)).where(Task.assigned_apprenant_id == current_user.id)
    ) or 0
    pending_apps = db.scalar(
        select(func.count(Application.id)).where(
            Application.apprenant_id == current_user.id,
            Application.status == ApplicationStatus.PENDING,
        )
    ) or 0
    active_packs = db.scalar(
        select(func.count(PackPurchase.id)).where(
            PackPurchase.apprenant_id == current_user.id,
            PackPurchase.status == PackPurchaseStatus.ACTIVE,
        )
    ) or 0
    score = compute_apprenant_score_breakdown(db, current_user)
    return DashboardStats(
        active_projects=active_missions,
        pending_applications=pending_apps,
        active_packs=active_packs,
        score_breakdown=score,
    )


@router.get("/decouvrir/listings", response_model=list[ListingPublic])
def discover_listings(
    db: DbSession, current_user: User = Depends(require_roles(UserRole.APPRENANT))
) -> list[ListingPublic]:
    """Page /apprenant/decouvrir."""
    from app.models.enums import ListingStatus

    listings = db.scalars(
        select(Listing).where(Listing.status == ListingStatus.OPEN).order_by(Listing.created_at.desc())
    ).all()
    return [ListingPublic.model_validate(l) for l in listings]


@router.post("/applications", response_model=ApplicationPublic, status_code=status.HTTP_201_CREATED)
def apply_to_listing(
    listing_id: UUID,
    payload: ApplicationCreate,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.APPRENANT)),
) -> ApplicationPublic:
    listing = db.get(Listing, listing_id)
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Annonce introuvable")

    existing = db.scalar(
        select(Application).where(
            Application.listing_id == listing_id,
            Application.apprenant_id == current_user.id,
        )
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Candidature déjà envoyée")

    application = Application(
        listing_id=listing_id,
        apprenant_id=current_user.id,
        cover_letter=payload.cover_letter,
    )
    db.add(application)
    listing.applications_count += 1
    db.commit()
    db.refresh(application)
    return application


@router.get("/activite/applications", response_model=list[ApplicationPublic])
def list_my_applications(
    db: DbSession, current_user: User = Depends(require_roles(UserRole.APPRENANT))
) -> list[ApplicationPublic]:
    """Page /apprenant/activite."""
    return list(
        db.scalars(
            select(Application)
            .where(Application.apprenant_id == current_user.id)
            .order_by(Application.created_at.desc())
        ).all()
    )


@router.get("/missions", response_model=list[ApprenantMissionDetail])
def list_my_missions(
    db: DbSession, current_user: User = Depends(require_roles(UserRole.APPRENANT))
) -> list[ApprenantMissionDetail]:
    """Page /apprenant/activite — missions en cours."""
    tasks = db.scalars(
        select(Task).where(Task.assigned_apprenant_id == current_user.id).order_by(Task.created_at.desc())
    ).all()
    return [_to_mission_detail(db, t) for t in tasks]


@router.get("/missions/{task_id}", response_model=ApprenantMissionDetail)
def get_mission(
    task_id: UUID,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.APPRENANT)),
) -> ApprenantMissionDetail:
    """Page /apprenant/missions/[id]."""
    task = db.get(Task, task_id)
    if not task or task.assigned_apprenant_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission introuvable")
    return _to_mission_detail(db, task)


@router.get("/packs", response_model=list[MentorPackPublic])
def browse_packs(
    db: DbSession, current_user: User = Depends(require_roles(UserRole.APPRENANT))
) -> list[MentorPackPublic]:
    """Page /apprenant/packs."""
    return list(db.scalars(select(MentorPack).where(MentorPack.is_active.is_(True))).all())


@router.get("/packs/purchases", response_model=list[PackPurchasePublic])
def list_my_pack_purchases(
    db: DbSession, current_user: User = Depends(require_roles(UserRole.APPRENANT))
) -> list[PackPurchasePublic]:
    return list(
        db.scalars(
            select(PackPurchase)
            .where(PackPurchase.apprenant_id == current_user.id)
            .order_by(PackPurchase.created_at.desc())
        ).all()
    )


@router.post("/packs/purchase", response_model=PackPurchasePublic, status_code=status.HTTP_201_CREATED)
def purchase_pack(
    payload: PackPurchaseCreate,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.APPRENANT)),
) -> PackPurchasePublic:
    pack = db.get(MentorPack, payload.pack_id)
    if not pack or not pack.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pack introuvable")
    purchase = PackPurchase(
        pack_id=pack.id,
        apprenant_id=current_user.id,
        mentor_id=pack.mentor_id,
        status=PackPurchaseStatus.PENDING_PAYMENT,
        amount_dzd=pack.price_dzd,
    )
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    return purchase


@router.get("/packs/{pack_id}", response_model=MentorPackPublic)
def get_pack_detail(
    pack_id: UUID,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.APPRENANT)),
) -> MentorPackPublic:
    """Page /apprenant/packs/[id]."""
    pack = db.get(MentorPack, pack_id)
    if not pack or not pack.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pack introuvable")
    return pack


@router.get("/progression", response_model=ScoreBreakdown)
def apprenant_progression(
    db: DbSession, current_user: User = Depends(require_roles(UserRole.APPRENANT))
) -> ScoreBreakdown:
    """Page /apprenant/progression."""
    return compute_apprenant_score_breakdown(db, current_user)


def _to_mission_detail(db: DbSession, task: Task) -> ApprenantMissionDetail:
    project = db.get(Project, task.project_id)
    deliverables = db.scalars(select(Deliverable).where(Deliverable.project_id == task.project_id)).all()
    submissions = db.scalars(select(Submission).where(Submission.task_id == task.id)).all()

    return ApprenantMissionDetail(
        id=task.id,
        project_id=task.project_id,
        project_title=project.title if project else "",
        project_description=project.description if project else "",
        project_progress_percent=project.progress_percent if project else 0,
        project_expected_deliverables=[d.title for d in deliverables],
        my_task=TaskPublic.model_validate(task),
        acceptance_criteria=task.acceptance_criteria or [],
        submissions=[SubmissionPublic.model_validate(s) for s in submissions],
    )
