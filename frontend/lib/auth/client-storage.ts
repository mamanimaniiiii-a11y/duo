"use client";

import {
  ACCESS_TOKEN_COOKIE,
  REFRESH_TOKEN_COOKIE,
} from "@/lib/auth/constants";

const COOKIE_OPTS = "path=/; SameSite=Lax";

export function setTokens(accessToken: string, refreshToken: string): void {
  document.cookie = `${ACCESS_TOKEN_COOKIE}=${encodeURIComponent(accessToken)}; ${COOKIE_OPTS}; max-age=3600`;
  document.cookie = `${REFRESH_TOKEN_COOKIE}=${encodeURIComponent(refreshToken)}; ${COOKIE_OPTS}; max-age=604800`;
}

export function clearTokens(): void {
  document.cookie = `${ACCESS_TOKEN_COOKIE}=; ${COOKIE_OPTS}; max-age=0`;
  document.cookie = `${REFRESH_TOKEN_COOKIE}=; ${COOKIE_OPTS}; max-age=0`;
}

export function getClientAccessToken(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie
    .split("; ")
    .find((row) => row.startsWith(`${ACCESS_TOKEN_COOKIE}=`));
  if (!match) return null;
  return decodeURIComponent(match.split("=").slice(1).join("="));
}
