from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import DeliverableStatus, ProjectStatus, TaskStatus
from app.schemas.common import ORMModel
from app.schemas.user import ApprenantSummary, MentorSummary, UserSummary


class ProjectCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10)
    category_id: UUID
    budget_dzd: int | None = Field(default=None, ge=0)
    deadline: datetime | None = None


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, min_length=10)
    category_id: UUID | None = None
    budget_dzd: int | None = Field(default=None, ge=0)
    deadline: datetime | None = None
    status: ProjectStatus | None = None
    progress_percent: int | None = Field(default=None, ge=0, le=100)


class DeliverablePublic(ORMModel):
    id: UUID
    project_id: UUID
    title: str
    status: DeliverableStatus
    file_ids: list[str]
    submitted_at: datetime | None = None
    approved_at: datetime | None = None


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(default="", max_length=2000)
    acceptance_criteria: list[str] = Field(default_factory=list)
    due_date: datetime | None = None
    sort_order: int | None = Field(default=None, ge=0)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    status: TaskStatus | None = None
    assigned_apprenant_id: UUID | None = None
    acceptance_criteria: list[str] | None = None
    due_date: datetime | None = None
    sort_order: int | None = Field(default=None, ge=0)


class TaskPublic(ORMModel):
    id: UUID
    project_id: UUID
    title: str
    description: str
    status: TaskStatus
    assigned_apprenant_id: UUID | None = None
    acceptance_criteria: list[str]
    due_date: datetime | None = None
    sort_order: int


class SubmissionPublic(ORMModel):
    id: UUID
    task_id: UUID
    content_url: str | None = None
    file_ids: list[str]
    submitted_at: datetime
    mentor_feedback: str | None = None


class ClientProjectDetail(ORMModel):
    id: UUID
    title: str
    description: str
    category_id: UUID
    status: ProjectStatus
    budget_dzd: int | None = None
    deadline: datetime | None = None
    progress_percent: int
    mentor: MentorSummary | None = None
    deliverables: list[DeliverablePublic]


class AvailableProjectPublic(ORMModel):
    """Projet publié par un client, disponible pour prise en charge par un mentor."""

    id: UUID
    title: str
    description: str
    category_id: UUID
    status: ProjectStatus
    budget_dzd: int | None = None
    deadline: datetime | None = None
    client: UserSummary


class MentorProjectDetail(ORMModel):
    id: UUID
    title: str
    description: str
    category_id: UUID
    status: ProjectStatus
    client: UserSummary
    progress_percent: int
    tasks: list[TaskPublic]
    deliverables: list[DeliverablePublic]
    assigned_apprenants: list[ApprenantSummary]


class ApprenantMissionDetail(ORMModel):
    id: UUID
    project_id: UUID
    project_title: str
    project_description: str
    project_progress_percent: int
    project_expected_deliverables: list[str]
    my_task: TaskPublic
    acceptance_criteria: list[str]
    submissions: list[SubmissionPublic]
