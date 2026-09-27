import { fetchApi } from "@/lib/api/client";
import {
  toAnnonce,
  toApplication,
  toApprenantSummary,
  toAvailableProject,
  toBoostOption,
  toDashboardStats,
  toMentorPack,
  toMentorProject,
  toScoreBreakdown,
  toTask,
} from "@/lib/api/mappers";
import type { Annonce } from "@/lib/types/annonce";
import type { Application } from "@/lib/types/application";
import type { BoostOption } from "@/lib/types/boost";
import type { DashboardStats } from "@/lib/types/dashboard";
import type { MentorPack } from "@/lib/types/pack";
import type { AvailableProject, MentorProjectDetail } from "@/lib/types/project";
import type { ScoreBreakdown } from "@/lib/types/review";
import type { ApprenantSummary } from "@/lib/types/user";

export async function getMentorDashboard(token: string): Promise<DashboardStats> {
  const record = await fetchApi<Record<string, unknown>>("/mentor/dashboard", {
    token,
  });
  return toDashboardStats(record);
}

export async function getMentorProjects(token: string): Promise<MentorProjectDetail[]> {
  const records = await fetchApi<Record<string, unknown>[]>("/mentor/projects", {
    token,
  });
  return records.map(toMentorProject);
}

export async function getMentorAvailableProjects(token: string): Promise<AvailableProject[]> {
  const records = await fetchApi<Record<string, unknown>[]>(
    "/mentor/projects/disponibles",
    { token },
  );
  return records.map(toAvailableProject);
}

export async function takeMentorProject(
  token: string,
  projectId: string,
): Promise<MentorProjectDetail> {
  const record = await fetchApi<Record<string, unknown>>(
    `/mentor/projects/${projectId}/prendre-en-charge`,
    { method: "POST", token },
  );
  return toMentorProject(record);
}

export async function getMentorProject(
  token: string,
  projectId: string,
): Promise<MentorProjectDetail> {
  const record = await fetchApi<Record<string, unknown>>(
    `/mentor/projects/${projectId}`,
    { token },
  );
  return toMentorProject(record);
}

export async function getMentorListings(token: string): Promise<Annonce[]> {
  const records = await fetchApi<Record<string, unknown>[]>(
    "/mentor/recrutement/listings",
    { token },
  );
  return records.map(toAnnonce);
}

export async function getMentorListingApplications(
  token: string,
  listingId: string,
): Promise<Application[]> {
  const records = await fetchApi<Record<string, unknown>[]>(
    `/mentor/recrutement/listings/${listingId}/applications`,
    { token },
  );
  return records.map(toApplication);
}

export async function getMentorApprenants(token: string): Promise<ApprenantSummary[]> {
  const records = await fetchApi<Record<string, unknown>[]>("/mentor/apprenants", {
    token,
  });
  return records.map(toApprenantSummary);
}

export async function getMentorPacks(token: string): Promise<MentorPack[]> {
  const records = await fetchApi<Record<string, unknown>[]>("/mentor/packs", {
    token,
  });
  return records.map(toMentorPack);
}

export async function getMentorProjectPacks(
  token: string,
  projectId: string,
): Promise<MentorPack[]> {
  const records = await fetchApi<Record<string, unknown>[]>(
    `/mentor/projects/${projectId}/packs`,
    { token },
  );
  return records.map(toMentorPack);
}

export async function getAssignableApprenants(token: string): Promise<ApprenantSummary[]> {
  const records = await fetchApi<Record<string, unknown>[]>("/mentor/apprenants/assignable", {
    token,
  });
  return records.map(toApprenantSummary);
}

export async function searchMentorApprenantsByUsername(
  token: string,
  username: string,
): Promise<ApprenantSummary[]> {
  const records = await fetchApi<Record<string, unknown>[]>(
    `/mentor/apprenants/search?username=${encodeURIComponent(username)}`,
    { token },
  );
  return records.map(toApprenantSummary);
}

export async function getMentorProjectEligibleApprenants(
  token: string,
  projectId: string,
): Promise<ApprenantSummary[]> {
  const records = await fetchApi<Record<string, unknown>[]>(
    `/mentor/projects/${projectId}/eligible-apprenants`,
    { token },
  );
  return records.map(toApprenantSummary);
}

export async function createMentorTask(
  token: string,
  projectId: string,
  payload: {
    title: string;
    description?: string;
    acceptanceCriteria?: string[];
  },
) {
  const record = await fetchApi<Record<string, unknown>>(
    `/mentor/projects/${projectId}/tasks`,
    {
      method: "POST",
      token,
      body: {
        title: payload.title,
        description: payload.description ?? "",
        acceptance_criteria: payload.acceptanceCriteria ?? [],
      },
    },
  );
  return toTask(record);
}

export async function updateMentorTask(
  token: string,
  projectId: string,
  taskId: string,
  payload: { assignedApprenantId?: string | null },
) {
  const record = await fetchApi<Record<string, unknown>>(
    `/mentor/projects/${projectId}/tasks/${taskId}`,
    {
      method: "PATCH",
      token,
      body: {
        assigned_apprenant_id: payload.assignedApprenantId ?? null,
      },
    },
  );
  return toTask(record);
}

export async function createMentorPack(
  token: string,
  payload: {
    title: string;
    description: string;
    priceDzd: number;
    durationDays: number;
    maxProjects: number;
    projectId?: string;
    features?: string[];
  },
): Promise<MentorPack> {
  const record = await fetchApi<Record<string, unknown>>("/mentor/packs", {
    method: "POST",
    token,
    body: {
      title: payload.title,
      description: payload.description,
      price_dzd: payload.priceDzd,
      duration_days: payload.durationDays,
      max_projects: payload.maxProjects,
      project_id: payload.projectId,
      features: payload.features ?? [],
    },
  });
  return toMentorPack(record);
}

export async function getMentorBoostOptions(token: string): Promise<BoostOption[]> {
  const records = await fetchApi<Record<string, unknown>[]>(
    "/mentor/boost/options",
    { token },
  );
  return records.map(toBoostOption);
}

export async function getMentorProgression(token: string): Promise<ScoreBreakdown> {
  const record = await fetchApi<Record<string, unknown>>("/mentor/progression", {
    token,
  });
  return toScoreBreakdown(record);
}
