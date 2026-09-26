from pydantic import BaseModel

from app.schemas.common import ScoreBreakdown


class DashboardStats(BaseModel):
    active_projects: int = 0
    completed_projects: int = 0
    pending_applications: int = 0
    open_listings: int = 0
    active_packs: int = 0
    unread_messages: int = 0
    unread_notifications: int = 0
    score_breakdown: ScoreBreakdown | None = None


class AdminDashboardStats(BaseModel):
    total_users: int = 0
    total_clients: int = 0
    total_mentors: int = 0
    total_apprenants: int = 0
    active_projects: int = 0
    open_disputes: int = 0
    pending_pack_purchases: int = 0
    pending_boost_subscriptions: int = 0
