import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { getMe } from "@/lib/api/auth";
import {
  ACCESS_TOKEN_COOKIE,
  REFRESH_TOKEN_COOKIE,
} from "@/lib/auth/constants";
import type { UserRole } from "@/lib/types/common";
import type { User } from "@/lib/types/user";

export async function getAccessToken(): Promise<string | undefined> {
  const store = await cookies();
  const value = store.get(ACCESS_TOKEN_COOKIE)?.value;
  return value ? decodeURIComponent(value) : undefined;
}

export async function getRefreshToken(): Promise<string | undefined> {
  const store = await cookies();
  const value = store.get(REFRESH_TOKEN_COOKIE)?.value;
  return value ? decodeURIComponent(value) : undefined;
}

export async function requireAuth(locale: string): Promise<{ token: string; user: User }> {
  const token = await getAccessToken();
  if (!token) {
    redirect(`/${locale}/auth/connexion`);
  }
  try {
    const user = await getMe(token);
    return { token, user };
  } catch {
    redirect(`/${locale}/auth/connexion`);
  }
}

export async function requireRole(
  locale: string,
  role: UserRole,
): Promise<{ token: string; user: User }> {
  const session = await requireAuth(locale);
  if (session.user.role !== role) {
    redirect(`/${locale}/auth/connexion`);
  }
  return session;
}

export async function getOptionalAuth(): Promise<{ token: string; user: User } | null> {
  const token = await getAccessToken();
  if (!token) return null;
  try {
    const user = await getMe(token);
    return { token, user };
  } catch {
    return null;
  }
}
