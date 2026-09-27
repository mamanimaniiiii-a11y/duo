import type { Account } from "@/lib/types/account";
import type { Annonce } from "@/lib/types/annonce";
import type { Application } from "@/lib/types/application";
import type { BoostOption, PremiumPlan } from "@/lib/types/boost";
import type { Category } from "@/lib/types/category";
import type { AdminDashboardStats, DashboardStats } from "@/lib/types/dashboard";
import type { Deliverable } from "@/lib/types/deliverable";
import type { Message } from "@/lib/types/message";
import type { Notification } from "@/lib/types/notification";
import type { MentorPack, PackPurchase } from "@/lib/types/pack";
import type {
  ApprenantMissionDetail,
  ClientProjectDetail,
  MentorProjectDetail,
} from "@/lib/types/project";
import type { ScoreBreakdown } from "@/lib/types/review";
import type { Submission, Task } from "@/lib/types/task";
import type {
  ApprenantProfile,
  ApprenantSummary,
  ClientSummary,
  MentorProfile,
  MentorSummary,
  User,
} from "@/lib/types/user";

function iso(value: string | null | undefined): string | undefined {
  return value ?? undefined;
}

export function toUser(record: Record<string, unknown>): User {
  return {
    id: String(record.id),
    email: String(record.email),
    username: String(record.username ?? ""),
    role: record.role as User["role"],
    displayName: String(record.display_name),
    avatarUrl: record.avatar_url ? String(record.avatar_url) : undefined,
    locale: record.locale as User["locale"],
    onboardingCompleted: Boolean(record.onboarding_completed),
    createdAt: String(record.created_at ?? ""),
  };
}

export function toMentorSummary(record: Record<string, unknown>): MentorSummary {
  return {
    id: String(record.id),
    username: String(record.username ?? ""),
    displayName: String(record.display_name),
    avatarUrl: record.avatar_url ? String(record.avatar_url) : undefined,
    skills: (record.skills as string[]) ?? [],
    score: Number(record.score ?? 0),
    isCertified: Boolean(record.is_certified),
  };
}

export function toApprenantSummary(record: Record<string, unknown>): ApprenantSummary {
  return {
    id: String(record.id),
    username: String(record.username ?? ""),
    displayName: String(record.display_name),
    avatarUrl: record.avatar_url ? String(record.avatar_url) : undefined,
    score: Number(record.score ?? 0),
  };
}

export function toClientSummary(record: Record<string, unknown>): ClientSummary {
  return {
    id: String(record.id),
    displayName: String(record.display_name),
    avatarUrl: record.avatar_url ? String(record.avatar_url) : undefined,
  };
}

export function toCategory(record: Record<string, unknown>): Category {
  const name = record.name as Record<string, string>;
  return {
    id: String(record.id),
    slug: String(record.slug),
    name: { fr: name.fr, en: name.en, ar: name.ar },
    isActive: Boolean(record.is_active),
    sortOrder: Number(record.sort_order ?? 0),
  };
}

export function toDeliverable(record: Record<string, unknown>): Deliverable {
  return {
    id: String(record.id),
    projectId: String(record.project_id),
    title: String(record.title),
    status: record.status as Deliverable["status"],
    fileIds: (record.file_ids as string[]) ?? [],
    submittedAt: iso(record.submitted_at as string | null),
    approvedAt: iso(record.approved_at as string | null),
  };
}

export function toTask(record: Record<string, unknown>): Task {
  return {
    id: String(record.id),
    projectId: String(record.project_id),
    title: String(record.title),
    description: String(record.description),
    status: record.status as Task["status"],
    assignedApprenantId: record.assigned_apprenant_id
      ? String(record.assigned_apprenant_id)
      : undefined,
    acceptanceCriteria: (record.acceptance_criteria as string[]) ?? [],
    dueDate: iso(record.due_date as string | null),
    sortOrder: Number(record.sort_order ?? 0),
  };
}

export function toSubmission(record: Record<string, unknown>): Submission {
  return {
    id: String(record.id),
    taskId: String(record.task_id),
    contentUrl: record.content_url ? String(record.content_url) : undefined,
    fileIds: (record.file_ids as string[]) ?? [],
    submittedAt: String(record.submitted_at),
    mentorFeedback: record.mentor_feedback
      ? String(record.mentor_feedback)
      : undefined,
  };
}

export function toClientProject(record: Record<string, unknown>): ClientProjectDetail {
  return {
    id: String(record.id),
    title: String(record.title),
    description: String(record.description),
    descriptionFormat: (record.description_format as ClientProjectDetail["descriptionFormat"]) ?? "standard",
    learnerComplexityLevel:
      (record.learner_complexity_level as ClientProjectDetail["learnerComplexityLevel"]) ??
      "beginner",
    categoryId: String(record.category_id),
    status: record.status as ClientProjectDetail["status"],
    budgetDzd: record.budget_dzd != null ? Number(record.budget_dzd) : undefined,
    deadline: iso(record.deadline as string | null),
    progressPercent: Number(record.progress_percent ?? 0),
    requiredSkills: (record.required_skills as string[]) ?? [],
    mentorMatchScore:
      record.mentor_match_score != null ? Number(record.mentor_match_score) : undefined,
    mentor: record.mentor
      ? toMentorSummary(record.mentor as Record<string, unknown>)
      : undefined,
    deliverables: ((record.deliverables as Record<string, unknown>[]) ?? []).map(
      toDeliverable,
    ),
  };
}

export function toMentorProject(record: Record<string, unknown>): MentorProjectDetail {
  return {
    id: String(record.id),
    title: String(record.title),
    description: String(record.description),
    descriptionFormat: (record.description_format as MentorProjectDetail["descriptionFormat"]) ?? "standard",
    learnerComplexityLevel:
      (record.learner_complexity_level as MentorProjectDetail["learnerComplexityLevel"]) ??
      "beginner",
    categoryId: String(record.category_id),
    status: record.status as MentorProjectDetail["status"],
    client: toClientSummary(record.client as Record<string, unknown>),
    progressPercent: Number(record.progress_percent ?? 0),
    tasks: ((record.tasks as Record<string, unknown>[]) ?? []).map(toTask),
    deliverables: ((record.deliverables as Record<string, unknown>[]) ?? []).map(
      toDeliverable,
    ),
    assignedApprenants: (
      (record.assigned_apprenants as Record<string, unknown>[]) ?? []
    ).map(toApprenantSummary),
  };
}

export function toAvailableProject(record: Record<string, unknown>) {
  return {
    id: String(record.id),
    title: String(record.title),
    description: String(record.description),
    categoryId: String(record.category_id),
    status: String(record.status),
    budgetDzd: record.budget_dzd != null ? Number(record.budget_dzd) : undefined,
    deadline: iso(record.deadline as string | null),
    requiredSkills: (record.required_skills as string[]) ?? [],
    matchScore: record.match_score != null ? Number(record.match_score) : undefined,
    client: toClientSummary(record.client as Record<string, unknown>),
  };
}

export function toMentorProjectMatch(record: Record<string, unknown>) {
  return {
    mentor: toMentorSummary(record.mentor as Record<string, unknown>),
    matchScore: Number(record.match_score ?? 0),
    skillsOverlap: Number(record.skills_overlap ?? 0),
    skillsMatchPercent: Number(record.skills_match_percent ?? 0),
    mentorScore: Number(record.mentor_score ?? 0),
  };
}

export function toAnnonce(record: Record<string, unknown>): Annonce {
  return {
    id: String(record.id),
    mentorId: String(record.mentor_id),
    title: String(record.title),
    description: String(record.description),
    requiredSkills: (record.required_skills as string[]) ?? [],
    projectId: record.project_id ? String(record.project_id) : undefined,
    status: record.status as Annonce["status"],
    applicationsCount: Number(record.applications_count ?? 0),
    createdAt: String(record.created_at),
    updatedAt: String(record.updated_at),
  };
}

export function toApplication(record: Record<string, unknown>): Application {
  return {
    id: String(record.id),
    annonceId: String(record.listing_id),
    apprenantId: String(record.apprenant_id),
    status: record.status as Application["status"],
    coverLetter: String(record.cover_letter),
    aiMatchScore: record.ai_match_score != null
      ? Number(record.ai_match_score)
      : undefined,
    createdAt: String(record.created_at),
    updatedAt: String(record.updated_at),
  };
}

export function toMentorPack(record: Record<string, unknown>): MentorPack {
  return {
    id: String(record.id),
    mentorId: String(record.mentor_id),
    projectId: record.project_id ? String(record.project_id) : undefined,
    title: String(record.title),
    description: String(record.description),
    priceDzd: Number(record.price_dzd ?? 0),
    durationDays: Number(record.duration_days ?? 0),
    maxProjects: Number(record.max_projects ?? 0),
    features: (record.features as string[]) ?? [],
    isActive: Boolean(record.is_active),
  };
}

export function toPackPurchase(record: Record<string, unknown>): PackPurchase {
  return {
    id: String(record.id),
    packId: String(record.pack_id),
    apprenantId: String(record.apprenant_id),
    mentorId: String(record.mentor_id),
    status: record.status as PackPurchase["status"],
    purchasedAt: iso(record.purchased_at as string | null),
    expiresAt: iso(record.expires_at as string | null),
    amountDzd: Number(record.amount_dzd ?? 0),
  };
}

export function toBoostOption(record: Record<string, unknown>): BoostOption {
  const label = record.label as Record<string, string>;
  return {
    id: String(record.id),
    label: { fr: label.fr, en: label.en, ar: label.ar },
    durationDays: Number(record.duration_days ?? 0),
    priceDzd: Number(record.price_dzd ?? 0),
    isActive: Boolean(record.is_active),
  };
}

export function toPremiumPlan(record: Record<string, unknown>): PremiumPlan {
  const label = record.label as Record<string, string>;
  return {
    id: String(record.id),
    label: { fr: label.fr, en: label.en, ar: label.ar },
    priceDzd: Number(record.price_dzd ?? 0),
    durationDays: Number(record.duration_days ?? 0),
    benefits: (record.benefits as string[]) ?? [],
    isActive: Boolean(record.is_active),
  };
}

export function toScoreBreakdown(record: Record<string, unknown>): ScoreBreakdown {
  return {
    total: Number(record.total ?? 0),
    projectsCompleted: Number(record.projects_completed ?? 0),
    apprenticesMentored: record.apprentices_mentored != null
      ? Number(record.apprentices_mentored)
      : undefined,
    averageRating: Number(record.average_rating ?? 0),
  };
}

export function toDashboardStats(record: Record<string, unknown>): DashboardStats {
  return {
    activeProjects: Number(record.active_projects ?? 0),
    completedProjects: Number(record.completed_projects ?? 0),
    pendingApplications: Number(record.pending_applications ?? 0),
    openListings: Number(record.open_listings ?? 0),
    activePacks: Number(record.active_packs ?? 0),
    unreadMessages: Number(record.unread_messages ?? 0),
    unreadNotifications: Number(record.unread_notifications ?? 0),
    scoreBreakdown: record.score_breakdown
      ? toScoreBreakdown(record.score_breakdown as Record<string, unknown>)
      : undefined,
  };
}

export function toAdminDashboardStats(
  record: Record<string, unknown>,
): AdminDashboardStats {
  return {
    totalUsers: Number(record.total_users ?? 0),
    totalClients: Number(record.total_clients ?? 0),
    totalMentors: Number(record.total_mentors ?? 0),
    totalApprenants: Number(record.total_apprenants ?? 0),
    activeProjects: Number(record.active_projects ?? 0),
    openDisputes: Number(record.open_disputes ?? 0),
    pendingPackPurchases: Number(record.pending_pack_purchases ?? 0),
    pendingBoostSubscriptions: Number(record.pending_boost_subscriptions ?? 0),
  };
}

export function toApprenantMission(
  record: Record<string, unknown>,
): ApprenantMissionDetail {
  return {
    id: String(record.id),
    projectId: String(record.project_id),
    projectTitle: String(record.project_title),
    projectDescription: String(record.project_description),
    projectProgressPercent: Number(record.project_progress_percent ?? 0),
    projectExpectedDeliverables:
      (record.project_expected_deliverables as string[]) ?? [],
    myTask: toTask(record.my_task as Record<string, unknown>),
    acceptanceCriteria: (record.acceptance_criteria as string[]) ?? [],
    submissions: ((record.submissions as Record<string, unknown>[]) ?? []).map(
      toSubmission,
    ),
  };
}

export function toMessage(record: Record<string, unknown>): Message {
  return {
    id: String(record.id),
    senderId: String(record.sender_id),
    recipientId: String(record.recipient_id),
    content: String(record.content),
    isRead: Boolean(record.is_read),
    createdAt: String(record.created_at),
  };
}

export function toNotification(record: Record<string, unknown>): Notification {
  return {
    id: String(record.id),
    title: String(record.title),
    body: String(record.body),
    link: record.link ? String(record.link) : undefined,
    isRead: Boolean(record.is_read),
    createdAt: String(record.created_at),
  };
}

export function toAccount(record: Record<string, unknown>): Account {
  const mentor = record.mentor_profile as Record<string, unknown> | null;
  const apprenant = record.apprenant_profile as Record<string, unknown> | null;
  const client = record.client_profile as Record<string, unknown> | null;

  return {
    id: String(record.id),
    email: String(record.email),
    username: String(record.username ?? ""),
    role: record.role as Account["role"],
    displayName: String(record.display_name),
    avatarUrl: record.avatar_url ? String(record.avatar_url) : undefined,
    locale: record.locale as Account["locale"],
    onboardingCompleted: Boolean(record.onboarding_completed),
    clientProfile: client
      ? {
          companyName: client.company_name ? String(client.company_name) : undefined,
          phone: client.phone ? String(client.phone) : undefined,
        }
      : undefined,
    mentorProfile: mentor
      ? {
          userId: String(mentor.user_id),
          bio: String(mentor.bio ?? ""),
          serviceCategoryIds: (mentor.service_category_ids as string[]) ?? [],
          skills: (mentor.skills as string[]) ?? [],
          score: Number(mentor.score ?? 0),
          isCertified: Boolean(mentor.is_certified),
          isPremium: Boolean(mentor.is_premium),
          boostStatus: mentor.boost_status as MentorProfile["boostStatus"],
          boostExpiresAt: iso(mentor.boost_expires_at as string | null),
          availabilityNote: mentor.availability_note
            ? String(mentor.availability_note)
            : undefined,
        }
      : undefined,
    apprenantProfile: apprenant
      ? {
          userId: String(apprenant.user_id),
          skills: (apprenant.skills as string[]) ?? [],
          careerGoal: String(apprenant.career_goal ?? ""),
          score: Number(apprenant.score ?? 0),
          canBecomeFreelance: Boolean(apprenant.can_become_freelance),
          portfolioProjectIds: (apprenant.portfolio_project_ids as string[]) ?? [],
        }
      : undefined,
    scoreBreakdown: record.score_breakdown
      ? toScoreBreakdown(record.score_breakdown as Record<string, unknown>)
      : undefined,
  };
}

export function toAdminUser(record: Record<string, unknown>) {
  return {
    id: String(record.id),
    email: String(record.email),
    role: String(record.role),
    displayName: String(record.display_name),
    isActive: Boolean(record.is_active),
    onboardingCompleted: Boolean(record.onboarding_completed),
  };
}

export function toDispute(record: Record<string, unknown>) {
  return {
    id: String(record.id),
    projectId: String(record.project_id),
    status: String(record.status),
    reason: String(record.reason ?? ""),
  };
}
