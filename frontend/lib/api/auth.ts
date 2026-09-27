import { getApiBaseUrl } from "@/lib/api/config";
import { ApiError, fetchApi } from "@/lib/api/client";
import { formatApiErrorDetail } from "@/lib/api/errors";
import { toUser } from "@/lib/api/mappers";
import type { Locale, UserRole } from "@/lib/types/common";
import type { User } from "@/lib/types/user";

export type TokenPair = {
  accessToken: string;
  refreshToken: string;
};

export type RegisterPayload = {
  email: string;
  password: string;
  displayName: string;
  role: UserRole;
  locale?: Locale;
  skills?: string[];
  careerGoal?: string;
};

export async function login(email: string, password: string): Promise<TokenPair> {
  const url = `${getApiBaseUrl()}/auth/login`;
  const body = new URLSearchParams({ username: email, password });
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });

  if (!response.ok) {
    let errorBody: unknown;
    try {
      errorBody = await response.json();
    } catch {
      errorBody = await response.text();
    }
    throw new ApiError(
      formatApiErrorDetail(errorBody) || "Connexion impossible",
      response.status,
      errorBody,
    );
  }

  const data = (await response.json()) as {
    access_token: string;
    refresh_token: string;
  };
  return {
    accessToken: data.access_token,
    refreshToken: data.refresh_token,
  };
}

export async function register(payload: RegisterPayload): Promise<User> {
  const body: Record<string, unknown> = {
    email: payload.email.trim().toLowerCase(),
    password: payload.password,
    display_name: payload.displayName.trim(),
    role: payload.role,
    locale: payload.locale ?? "fr",
  };

  if (payload.role === "apprenant") {
    body.skills = payload.skills ?? [];
    body.career_goal = payload.careerGoal ?? "";
  }

  const record = await fetchApi<Record<string, unknown>>("/auth/register", {
    method: "POST",
    body,
  });
  return toUser(record);
}

export async function getMe(token: string): Promise<User> {
  const record = await fetchApi<Record<string, unknown>>("/auth/me", { token });
  return toUser(record);
}

export async function refreshTokens(refreshToken: string): Promise<TokenPair> {
  const data = await fetchApi<{
    access_token: string;
    refresh_token: string;
  }>("/auth/refresh", {
    method: "POST",
    body: { refresh_token: refreshToken },
  });
  return {
    accessToken: data.access_token,
    refreshToken: data.refresh_token,
  };
}
