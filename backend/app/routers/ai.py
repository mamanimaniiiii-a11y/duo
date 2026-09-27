from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.deps import DbSession, require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.ai import AiGapRecommendation, AiTaskBreakdown, TaskBreakdownApplyRequest
from app.schemas.project import TaskPublic
from app.services.ai.gap_analysis import generate_gap_analysis
from app.services.ai.task_breakdown import apply_task_breakdown, generate_task_breakdown_preview

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post(
    "/projects/{project_id}/task-breakdown",
    response_model=AiTaskBreakdown,
    summary="Découpage IA des tâches (preview)",
    description=(
        "Propose un découpage en sous-tâches pour apprenants. "
        "La langue de sortie suit la locale du mentor connecté (fr/ar/en). "
        "Ne persiste rien en base — utiliser task-breakdown/apply pour valider."
    ),
)
def preview_task_breakdown(
    project_id: UUID,
    db: DbSession,
    task_count: int | None = Query(
        default=None,
        ge=3,
        le=8,
        description="Nombre exact de sous-tâches souhaité (3 à 8). Omis = le modèle choisit entre 3 et 8.",
    ),
    current_user: User = Depends(require_roles(UserRole.MENTOR)),
) -> AiTaskBreakdown:
    """Page /mentor/projets/[id] — bouton « Proposer un découpage IA »."""
    return generate_task_breakdown_preview(
        db,
        project_id,
        current_user,
        task_count=task_count,
    )


@router.post(
    "/projects/{project_id}/task-breakdown/apply",
    response_model=list[TaskPublic],
    status_code=status.HTTP_201_CREATED,
    summary="Appliquer le découpage IA validé par le mentor",
)
def apply_task_breakdown_endpoint(
    project_id: UUID,
    payload: TaskBreakdownApplyRequest,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.MENTOR)),
) -> list[TaskPublic]:
    """Crée les tâches en base après validation/édition par le mentor."""
    return apply_task_breakdown(db, project_id, current_user, payload)


@router.get(
    "/apprenant/gap-analysis",
    response_model=AiGapRecommendation,
    summary="Analyse de lacunes et recommandations (preview)",
    description=(
        "Identifie les lacunes de compétences et recommande des projets liés à des annonces ouvertes. "
        "La langue de sortie suit la locale de l'apprenant connecté (fr/ar/en). "
        "Recommandation uniquement : aucune assignation automatique."
    ),
)
def apprenant_gap_analysis(
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.APPRENANT)),
) -> AiGapRecommendation:
    """Page /apprenant/decouvrir — analyse IA des lacunes."""
    return generate_gap_analysis(db, current_user)
