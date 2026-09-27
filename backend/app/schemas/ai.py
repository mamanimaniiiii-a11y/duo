from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SuggestedTask(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=20, max_length=2000)
    acceptance_criteria: list[str] = Field(min_length=2, max_length=5)
    due_date: datetime | None = None
    sort_order: int = Field(ge=0)


class AiTaskBreakdown(BaseModel):
    suggested_tasks: list[SuggestedTask] = Field(min_length=3, max_length=8)


class TaskBreakdownApplyRequest(BaseModel):
    suggested_tasks: list[SuggestedTask] = Field(min_length=3, max_length=8)


class SuggestedProjectIdea(BaseModel):
    title: str = Field(min_length=5, max_length=120)
    description: str = Field(min_length=40, max_length=600)
    target_skills: list[str] = Field(min_length=1, max_length=6)


class AiGapRecommendation(BaseModel):
    skill_gap: str = Field(min_length=20, max_length=2000)
    recommended_project_ids: list[UUID] = Field(default_factory=list, max_length=5)
    explanation: str = Field(min_length=80, max_length=3000)
    suggested_project_ideas: list[SuggestedProjectIdea] = Field(default_factory=list, max_length=3)
