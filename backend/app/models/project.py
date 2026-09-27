import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enum_column import pg_enum
from app.models.enums import (
    DeliverableStatus,
    LearnerComplexityLevel,
    ProjectDescriptionFormat,
    ProjectStatus,
    TaskStatus,
)


class Project(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "projects"

    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    mentor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    description_format: Mapped[ProjectDescriptionFormat] = mapped_column(
        pg_enum(ProjectDescriptionFormat, name="project_description_format"),
        default=ProjectDescriptionFormat.STANDARD,
        nullable=False,
    )
    learner_complexity_level: Mapped[LearnerComplexityLevel] = mapped_column(
        pg_enum(LearnerComplexityLevel, name="learner_complexity_level"),
        default=LearnerComplexityLevel.BEGINNER,
        nullable=False,
    )
    status: Mapped[ProjectStatus] = mapped_column(
        pg_enum(ProjectStatus, name="project_status"), default=ProjectStatus.DRAFT, nullable=False
    )
    budget_dzd: Mapped[int | None] = mapped_column(Integer, nullable=True)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    required_skills: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)

    category = relationship("Category", back_populates="projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    deliverables = relationship("Deliverable", back_populates="project", cascade="all, delete-orphan")
    listings = relationship("Listing", back_populates="project")


class Task(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "tasks"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        pg_enum(TaskStatus, name="task_status"), default=TaskStatus.TODO, nullable=False
    )
    assigned_apprenant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    acceptance_criteria: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    project = relationship("Project", back_populates="tasks")
    submissions = relationship("Submission", back_populates="task", cascade="all, delete-orphan")


class Deliverable(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "deliverables"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[DeliverableStatus] = mapped_column(
        pg_enum(DeliverableStatus, name="deliverable_status"),
        default=DeliverableStatus.PENDING,
        nullable=False,
    )
    file_ids: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project = relationship("Project", back_populates="deliverables")


class Submission(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "submissions"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_ids: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    mentor_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)

    task = relationship("Task", back_populates="submissions")
