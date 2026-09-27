import { fetchApi } from "@/lib/api/client";
import { toAccount } from "@/lib/api/mappers";
import type { Account } from "@/lib/types/account";
import type { Locale } from "@/lib/types/common";

export async function getAccount(token: string): Promise<Account> {
  const record = await fetchApi<Record<string, unknown>>("/account", { token });
  return toAccount(record);
}

export async function updateAccount(
  token: string,
  payload: { displayName?: string; avatarUrl?: string; locale?: Locale },
): Promise<Account> {
  const record = await fetchApi<Record<string, unknown>>("/account", {
    method: "PATCH",
    token,
    body: {
      display_name: payload.displayName,
      avatar_url: payload.avatarUrl,
      locale: payload.locale,
    },
  });
  return toAccount(record);
}

export async function completeOnboarding(token: string): Promise<void> {
  await fetchApi("/account/onboarding/complete", {
    method: "POST",
    token,
    body: {},
  });
}

export async function updateMentorProfile(
  token: string,
  payload: {
    bio?: string;
    availabilityNote?: string;
    serviceCategoryIds?: string[];
    skills?: string[];
  },
): Promise<Account> {
  const record = await fetchApi<Record<string, unknown>>("/account/mentor-profile", {
    method: "PATCH",
    token,
    body: {
      bio: payload.bio,
      availability_note: payload.availabilityNote,
      service_category_ids: payload.serviceCategoryIds,
      skills: payload.skills,
    },
  });
  return toAccount(record);
}

export async function updateApprenantProfile(
  token: string,
  payload: { skills?: string[]; careerGoal?: string },
): Promise<Account> {
  const record = await fetchApi<Record<string, unknown>>("/account/apprenant-profile", {
    method: "PATCH",
    token,
    body: {
      skills: payload.skills,
      career_goal: payload.careerGoal,
    },
  });
  return toAccount(record);
}
