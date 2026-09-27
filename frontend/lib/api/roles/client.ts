import { fetchApi } from "@/lib/api/client";
import { toClientProject, toDashboardStats, toMentorProjectMatch } from "@/lib/api/mappers";
import type { DashboardStats } from "@/lib/types/dashboard";
import type { ClientProjectDetail, MentorProjectMatch } from "@/lib/types/project";

export async function getClientDashboard(token: string): Promise<DashboardStats> {
  const record = await fetchApi<Record<string, unknown>>("/client/dashboard", {
    token,
  });
  return toDashboardStats(record);
}

export async function getClientProjects(token: string): Promise<ClientProjectDetail[]> {
  const records = await fetchApi<Record<string, unknown>[]>("/client/projects", {
    token,
  });
  return records.map(toClientProject);
}

export async function getClientProject(
  token: string,
  projectId: string,
): Promise<ClientProjectDetail> {
  const record = await fetchApi<Record<string, unknown>>(
    `/client/projects/${projectId}`,
    { token },
  );
  return toClientProject(record);
}

export async function createClientProject(
  token: string,
  payload: {
    title: string;
    description: string;
    descriptionFormat: string;
    learnerComplexityLevel: string;
    categoryId: string;
    requiredSkills?: string[];
    budgetDzd?: number;
    deadline?: string;
  },
): Promise<ClientProjectDetail> {
  const record = await fetchApi<Record<string, unknown>>("/client/projects", {
    method: "POST",
    token,
    body: {
      title: payload.title,
      description: payload.description,
      description_format: payload.descriptionFormat,
      learner_complexity_level: payload.learnerComplexityLevel,
      category_id: payload.categoryId,
      required_skills: payload.requiredSkills ?? [],
      budget_dzd: payload.budgetDzd,
      deadline: payload.deadline,
    },
  });
  return toClientProject(record);
}

export async function assignClientProjectMentor(
  token: string,
  projectId: string,
  mentorId: string,
): Promise<ClientProjectDetail> {
  const record = await fetchApi<Record<string, unknown>>(
    `/client/projects/${projectId}/assign-mentor`,
    {
      method: "POST",
      token,
      body: { mentor_id: mentorId },
    },
  );
  return toClientProject(record);
}

export async function getClientProjectMentorMatches(
  token: string,
  projectId: string,
): Promise<MentorProjectMatch[]> {
  const records = await fetchApi<Record<string, unknown>[]>(
    `/client/projects/${projectId}/mentor-matches`,
    { token },
  );
  return records.map(toMentorProjectMatch);
}

export async function updateClientProject(
  token: string,
  projectId: string,
  payload: Record<string, unknown>,
): Promise<ClientProjectDetail> {
  const record = await fetchApi<Record<string, unknown>>(
    `/client/projects/${projectId}`,
    { method: "PATCH", token, body: payload },
  );
  return toClientProject(record);
}

export async function publishClientProject(
  token: string,
  projectId: string,
): Promise<ClientProjectDetail> {
  const record = await fetchApi<Record<string, unknown>>(
    `/client/projects/${projectId}/publish`,
    { method: "POST", token },
  );
  return toClientProject(record);
}
