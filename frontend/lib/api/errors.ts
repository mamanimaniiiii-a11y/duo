import { ApiError } from "@/lib/api/client";

type ValidationIssue = {
  loc?: (string | number)[];
  msg?: string;
};

/** Extrait le message lisible renvoyé par FastAPI (detail string ou tableau de validation). */
export function formatApiErrorDetail(body: unknown): string {
  if (typeof body === "string") return body;
  if (!body || typeof body !== "object" || !("detail" in body)) {
    return "Une erreur est survenue";
  }

  const detail = (body as { detail: unknown }).detail;

  if (typeof detail === "string") return detail;

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") return item;
        if (item && typeof item === "object") {
          const issue = item as ValidationIssue;
          const field = issue.loc?.filter((part) => part !== "body").join(".");
          const msg = issue.msg ?? JSON.stringify(item);
          return field ? `${field} : ${msg}` : msg;
        }
        return JSON.stringify(item);
      })
      .join(" · ");
  }

  return JSON.stringify(detail);
}

export function getApiErrorMessage(
  error: unknown,
  context: "login" | "register" = "login",
): string {
  if (!(error instanceof ApiError)) {
    return error instanceof Error ? error.message : "Une erreur inattendue est survenue";
  }

  const detail = formatApiErrorDetail(error.body);

  if (error.status === 409) {
    return detail || "Un compte existe déjà avec cet email.";
  }

  if (error.status === 422) {
    return detail || "Données invalides. Vérifiez les champs du formulaire.";
  }

  if (error.status === 401) {
    return context === "register"
      ? `Inscription réussie, mais la connexion automatique a échoué : ${detail || "identifiants refusés"}`
      : detail || "Email ou mot de passe incorrect.";
  }

  if (detail) return detail;

  return error.message;
}
