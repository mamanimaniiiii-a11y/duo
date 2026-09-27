from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.category import Category
from app.models.enums import Locale, ProjectStatus, TaskStatus
from app.models.project import Deliverable, Project, Task
from app.models.user import User
from app.schemas.ai import AiTaskBreakdown, SuggestedTask, TaskBreakdownApplyRequest
from app.schemas.project import TaskPublic
from app.services.ai.ai_provider import AIProvider
from app.services.ai.prompts import (
    build_task_breakdown_json_schema,
    build_task_breakdown_system_prompt,
    build_task_breakdown_user_prompt,
    resolve_output_locale,
    resolve_task_count_bounds,
)


def _get_mentor_project(db: Session, project_id: UUID, mentor_id: UUID) -> Project:
    project = db.get(Project, project_id)
    if not project or project.mentor_id != mentor_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable")
    if project.status not in (ProjectStatus.ASSIGNED, ProjectStatus.IN_PROGRESS):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Le découpage IA est disponible après prise en charge du projet (statut assigned ou in_progress)",
        )
    return project


def _build_user_prompt(db: Session, project: Project, task_count: int | None = None) -> str:
    category = db.get(Category, project.category_id)
    deliverables = db.scalars(
        select(Deliverable).where(Deliverable.project_id == project.id)
    ).all()
    existing_tasks = db.scalars(
        select(Task).where(Task.project_id == project.id).order_by(Task.sort_order)
    ).all()
    assigned_count = db.scalar(
        select(func.count(Task.id)).where(
            Task.project_id == project.id,
            Task.assigned_apprenant_id.is_not(None),
        )
    ) or 0

    deadline = project.deadline.isoformat() if project.deadline else None
    return build_task_breakdown_user_prompt(
        project_title=project.title,
        category_name=category.name_fr if category else "—",
        category_slug=category.slug if category else "—",
        project_description=project.description,
        budget_dzd=project.budget_dzd,
        project_deadline=deadline,
        deliverables=[{"title": d.title, "status": d.status.value} for d in deliverables],
        assigned_apprenants_count=assigned_count,
        existing_tasks=[{"title": t.title, "sort_order": t.sort_order} for t in existing_tasks],
        task_count=task_count,
        description_format=project.description_format.value,
        learner_complexity_level=project.learner_complexity_level.value,
    )


def validate_suggested_tasks(
    tasks: list[SuggestedTask],
    project_deadline: datetime | None,
    task_count: int | None = None,
) -> None:
    min_tasks, max_tasks = resolve_task_count_bounds(task_count)
    if not (min_tasks <= len(tasks) <= max_tasks):
        if task_count is not None:
            detail = f"Le découpage doit contenir exactement {task_count} sous-tâches"
        else:
            detail = "Le découpage doit contenir entre 3 et 8 sous-tâches"
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )

    sort_orders = [task.sort_order for task in tasks]
    if len(set(sort_orders)) != len(sort_orders):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Chaque sort_order doit être unique",
        )
    expected = list(range(len(tasks)))
    if sorted(sort_orders) != expected:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Les sort_order doivent être consécutifs à partir de 0",
        )

    for task in tasks:
        for criterion in task.acceptance_criteria:
            if len(criterion) < 10:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Chaque critère d'acceptation doit faire au moins 10 caractères",
                )
        if task.due_date and project_deadline and task.due_date > project_deadline:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Une due_date dépasse la deadline du projet",
            )


def generate_task_breakdown_preview(
    db: Session,
    project_id: UUID,
    mentor: User,
    task_count: int | None = None,
) -> AiTaskBreakdown:
    settings = get_settings()
    if not settings.ai_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Les fonctionnalités IA sont désactivées",
        )

    project = _get_mentor_project(db, project_id, mentor.id)
    locale = resolve_output_locale(mentor.locale.value if mentor.locale else Locale.FR.value)
    system_prompt = build_task_breakdown_system_prompt(
        locale,
        task_count=task_count,
        learner_complexity_level=project.learner_complexity_level.value,
    )
    user_prompt = _build_user_prompt(db, project, task_count=task_count)
    json_schema = build_task_breakdown_json_schema(task_count)

    try:
        client = AIProvider()
        raw = client.complete_json_schema(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema_name="task_breakdown",
            schema=json_schema,
        )
        breakdown = AiTaskBreakdown.model_validate(raw)
        validate_suggested_tasks(
            breakdown.suggested_tasks,
            project.deadline,
            task_count=task_count,
        )
        return breakdown
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Échec du découpage IA : {exc}",
        ) from exc


def apply_task_breakdown(
    db: Session,
    project_id: UUID,
    mentor: User,
    payload: TaskBreakdownApplyRequest,
) -> list[TaskPublic]:
    project = _get_mentor_project(db, project_id, mentor.id)
    existing_count = db.scalar(
        select(func.count(Task.id)).where(Task.project_id == project.id)
    ) or 0
    if existing_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce projet a déjà des tâches enregistrées. Assignez-les aux apprenants sans regénérer.",
        )
    validate_suggested_tasks(payload.suggested_tasks, project.deadline)

    created: list[Task] = []
    for item in sorted(payload.suggested_tasks, key=lambda t: t.sort_order):
        task = Task(
            project_id=project.id,
            title=item.title,
            description=item.description,
            acceptance_criteria=item.acceptance_criteria,
            due_date=item.due_date,
            sort_order=item.sort_order,
            status=TaskStatus.TODO,
        )
        db.add(task)
        created.append(task)

    if project.status == ProjectStatus.ASSIGNED:
        project.status = ProjectStatus.IN_PROGRESS

    db.commit()
    for task in created:
        db.refresh(task)

    return [TaskPublic.model_validate(task) for task in created]
