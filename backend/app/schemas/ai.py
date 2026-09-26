from datetime import datetime

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
