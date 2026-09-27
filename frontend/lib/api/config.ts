const DEFAULT_API_URL = "http://localhost:8000/api/v1";

/**
 * URL de base de l'API FastAPI (sans slash final).
 * Définie via NEXT_PUBLIC_API_URL dans .env.local
 */
export function getApiBaseUrl(): string {
  const url = process.env.NEXT_PUBLIC_API_URL?.trim() || DEFAULT_API_URL;
  return url.replace(/\/$/, "");
}
