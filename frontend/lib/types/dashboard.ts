import type { ScoreBreakdown } from "./review";

export interface DashboardStats {
  activeProjects: number;
  completedProjects: number;
  pendingApplications: number;
  openListings: number;
  activePacks: number;
  unreadMessages: number;
  unreadNotifications: number;
  scoreBreakdown?: ScoreBreakdown;
}

export interface AdminDashboardStats {
  totalUsers: number;
  totalClients: number;
  totalMentors: number;
  totalApprenants: number;
  activeProjects: number;
  openDisputes: number;
  pendingPackPurchases: number;
  pendingBoostSubscriptions: number;
}
