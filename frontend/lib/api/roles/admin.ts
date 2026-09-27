import { fetchApi } from "@/lib/api/client";
import {
  toAdminDashboardStats,
  toAdminUser,
  toBoostOption,
  toCategory,
  toDispute,
  toPremiumPlan,
} from "@/lib/api/mappers";
import type { BoostOption, PremiumPlan } from "@/lib/types/boost";
import type { Category } from "@/lib/types/category";
import type { AdminDashboardStats } from "@/lib/types/dashboard";

export async function getAdminDashboard(token: string): Promise<AdminDashboardStats> {
  const record = await fetchApi<Record<string, unknown>>("/admin/dashboard", {
    token,
  });
  return toAdminDashboardStats(record);
}

export async function getAdminUsers(token: string) {
  const records = await fetchApi<Record<string, unknown>[]>(
    "/admin/utilisateurs",
    { token },
  );
  return records.map(toAdminUser);
}

export async function toggleAdminUserActive(
  token: string,
  userId: string,
): Promise<void> {
  await fetchApi(`/admin/utilisateurs/${userId}/toggle-active`, {
    method: "PATCH",
    token,
  });
}

export async function getAdminDisputes(token: string) {
  const records = await fetchApi<Record<string, unknown>[]>("/admin/litiges", {
    token,
  });
  return records.map(toDispute);
}

export async function getAdminCategories(token: string): Promise<Category[]> {
  const records = await fetchApi<Record<string, unknown>[]>(
    "/admin/configuration/categories",
    { token },
  );
  return records.map(toCategory);
}

export async function getAdminBoostOptions(token: string): Promise<BoostOption[]> {
  const records = await fetchApi<Record<string, unknown>[]>(
    "/admin/boost-premium/boost-options",
    { token },
  );
  return records.map(toBoostOption);
}

export async function getAdminPremiumPlans(token: string): Promise<PremiumPlan[]> {
  const records = await fetchApi<Record<string, unknown>[]>(
    "/admin/boost-premium/premium-plans",
    { token },
  );
  return records.map(toPremiumPlan);
}
