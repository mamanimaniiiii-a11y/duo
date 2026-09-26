from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select

from app.core.deps import DbSession, require_roles
from app.models.boost import BoostOption, BoostSubscription, PremiumPlan, PremiumSubscription
from app.models.category import Category
from app.models.enums import DisputeStatus, PackPurchaseStatus, SubscriptionStatus, UserRole
from app.models.pack import PackPurchase
from app.models.support import Dispute
from app.models.user import User
from app.schemas.boost import BoostOptionCreate, BoostOptionPublic, PremiumPlanCreate, PremiumPlanPublic
from app.schemas.category import CategoryCreate, CategoryPublic, CategoryUpdate
from app.schemas.common import LocalizedString, MessageResponse
from app.schemas.dashboard import AdminDashboardStats
from app.services.serializers import category_to_public

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)


@router.get("/dashboard", response_model=AdminDashboardStats)
def admin_dashboard(
    db: DbSession, current_user: User = Depends(require_roles(UserRole.ADMIN))
) -> AdminDashboardStats:
    """Page /admin/dashboard."""
    return AdminDashboardStats(
        total_users=db.scalar(select(func.count(User.id))) or 0,
        total_clients=db.scalar(select(func.count(User.id)).where(User.role == UserRole.CLIENT)) or 0,
        total_mentors=db.scalar(select(func.count(User.id)).where(User.role == UserRole.MENTOR)) or 0,
        total_apprenants=db.scalar(select(func.count(User.id)).where(User.role == UserRole.APPRENANT)) or 0,
        open_disputes=db.scalar(
            select(func.count(Dispute.id)).where(Dispute.status.in_([DisputeStatus.OPEN, DisputeStatus.IN_REVIEW]))
        ) or 0,
        pending_pack_purchases=db.scalar(
            select(func.count(PackPurchase.id)).where(
                PackPurchase.status.in_([PackPurchaseStatus.PENDING_PAYMENT, PackPurchaseStatus.PENDING_ADMIN])
            )
        ) or 0,
        pending_boost_subscriptions=db.scalar(
            select(func.count(BoostSubscription.id)).where(
                BoostSubscription.status.in_([SubscriptionStatus.PENDING_PAYMENT, SubscriptionStatus.PENDING_ADMIN])
            )
        ) or 0,
    )


@router.get("/utilisateurs", response_model=list[dict])
def list_users(
    db: DbSession, current_user: User = Depends(require_roles(UserRole.ADMIN))
) -> list[dict]:
    """Page /admin/utilisateurs."""
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    return [
        {
            "id": str(u.id),
            "email": u.email,
            "role": u.role.value,
            "display_name": u.display_name,
            "is_active": u.is_active,
            "onboarding_completed": u.onboarding_completed,
        }
        for u in users
    ]


@router.patch("/utilisateurs/{user_id}/toggle-active", response_model=MessageResponse)
def toggle_user_active(
    user_id: UUID,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> MessageResponse:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")
    user.is_active = not user.is_active
    db.commit()
    return MessageResponse(message="Statut utilisateur mis à jour")


@router.get("/litiges", response_model=list[dict])
def list_disputes(
    db: DbSession, current_user: User = Depends(require_roles(UserRole.ADMIN))
) -> list[dict]:
    """Page /admin/litiges."""
    disputes = db.scalars(select(Dispute).order_by(Dispute.created_at.desc())).all()
    return [
        {
            "id": str(d.id),
            "project_id": str(d.project_id),
            "status": d.status.value,
            "reason": d.reason,
        }
        for d in disputes
    ]


@router.get("/configuration/categories", response_model=list[CategoryPublic])
def admin_list_categories(
    db: DbSession, current_user: User = Depends(require_roles(UserRole.ADMIN))
) -> list[CategoryPublic]:
    """Page /admin/configuration."""
    categories = db.scalars(select(Category).order_by(Category.sort_order)).all()
    return [category_to_public(c) for c in categories]


@router.post("/configuration/categories", response_model=CategoryPublic, status_code=status.HTTP_201_CREATED)
def admin_create_category(
    payload: CategoryCreate,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> CategoryPublic:
    category = Category(
        slug=payload.slug,
        name_fr=payload.name.fr,
        name_en=payload.name.en,
        name_ar=payload.name.ar,
        sort_order=payload.sort_order,
        is_active=payload.is_active,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category_to_public(category)


@router.patch("/configuration/categories/{category_id}", response_model=CategoryPublic)
def admin_update_category(
    category_id: UUID,
    payload: CategoryUpdate,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> CategoryPublic:
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catégorie introuvable")
    if payload.name:
        category.name_fr = payload.name.fr
        category.name_en = payload.name.en
        category.name_ar = payload.name.ar
    if payload.sort_order is not None:
        category.sort_order = payload.sort_order
    if payload.is_active is not None:
        category.is_active = payload.is_active
    db.commit()
    db.refresh(category)
    return category_to_public(category)


@router.get("/boost-premium/boost-options", response_model=list[BoostOptionPublic])
def admin_list_boost_options(
    db: DbSession, current_user: User = Depends(require_roles(UserRole.ADMIN))
) -> list[BoostOptionPublic]:
    """Page /admin/boost-premium."""
    options = db.scalars(select(BoostOption).order_by(BoostOption.created_at.desc())).all()
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


@router.post("/boost-premium/boost-options", response_model=BoostOptionPublic, status_code=status.HTTP_201_CREATED)
def admin_create_boost_option(
    payload: BoostOptionCreate,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> BoostOptionPublic:
    option = BoostOption(
        label_fr=payload.label.fr,
        label_en=payload.label.en,
        label_ar=payload.label.ar,
        duration_days=payload.duration_days,
        price_dzd=payload.price_dzd,
        is_active=payload.is_active,
    )
    db.add(option)
    db.commit()
    db.refresh(option)
    return BoostOptionPublic(
        id=option.id,
        label=payload.label,
        duration_days=option.duration_days,
        price_dzd=option.price_dzd,
        is_active=option.is_active,
    )


@router.get("/boost-premium/premium-plans", response_model=list[PremiumPlanPublic])
def admin_list_premium_plans(
    db: DbSession, current_user: User = Depends(require_roles(UserRole.ADMIN))
) -> list[PremiumPlanPublic]:
    plans = db.scalars(select(PremiumPlan).order_by(PremiumPlan.created_at.desc())).all()
    return [
        PremiumPlanPublic(
            id=p.id,
            label=LocalizedString(fr=p.label_fr, en=p.label_en, ar=p.label_ar),
            price_dzd=p.price_dzd,
            duration_days=p.duration_days,
            benefits=p.benefits or [],
            is_active=p.is_active,
        )
        for p in plans
    ]


@router.post("/boost-premium/premium-plans", response_model=PremiumPlanPublic, status_code=status.HTTP_201_CREATED)
def admin_create_premium_plan(
    payload: PremiumPlanCreate,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> PremiumPlanPublic:
    plan = PremiumPlan(
        label_fr=payload.label.fr,
        label_en=payload.label.en,
        label_ar=payload.label.ar,
        price_dzd=payload.price_dzd,
        duration_days=payload.duration_days,
        benefits=payload.benefits,
        is_active=payload.is_active,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return PremiumPlanPublic(
        id=plan.id,
        label=payload.label,
        price_dzd=plan.price_dzd,
        duration_days=plan.duration_days,
        benefits=plan.benefits or [],
        is_active=plan.is_active,
    )
