import { formatApiErrorDetail } from "@/lib/api/errors";
import { getApiBaseUrl } from "./config";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly body?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export type FetchApiOptions = {
  method?: "GET" | "POST" | "PATCH" | "PUT" | "DELETE";
  body?: unknown;
  token?: string;
  headers?: Record<string, string>;
  cache?: RequestCache;
};

/**
 * Client HTTP minimal vers l'API Duo.
 * Préfixe automatiquement NEXT_PUBLIC_API_URL ; path doit commencer par / (ex. /public/categories).
 */
export async function fetchApi<T>(
  path: string,
  options: FetchApiOptions = {},
): Promise<T> {
  const {
    method = "GET",
    body,
    token,
    headers = {},
    cache = "no-store",
  } = options;

  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const url = `${getApiBaseUrl()}${normalizedPath}`;

  const requestHeaders: Record<string, string> = {
    Accept: "application/json",
    ...headers,
  };

  let requestBody: string | undefined;
  if (body !== undefined) {
    requestHeaders["Content-Type"] = "application/json";
    requestBody = JSON.stringify(body);
  }

  if (token) {
    requestHeaders.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    method,
    headers: requestHeaders,
    body: requestBody,
    cache,
  });

  if (!response.ok) {
    let errorBody: unknown;
    const contentType = response.headers.get("content-type") ?? "";
    if (contentType.includes("application/json")) {
      errorBody = await response.json();
    } else {
      errorBody = await response.text();
    }
    const detail = formatApiErrorDetail(errorBody);
    throw new ApiError(
      detail || `Requête API échouée (${response.status}) : ${normalizedPath}`,
      response.status,
      errorBody,
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}
