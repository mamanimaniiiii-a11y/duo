import { getApiErrorMessage } from "@/lib/api/errors";

type ApiErrorBoxProps = {
  error: unknown;
  title?: string;
};

export function ApiErrorBox({ error, title = "Erreur" }: ApiErrorBoxProps) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
      <p className="font-semibold">{title}</p>
      <p className="mt-1">{getApiErrorMessage(error)}</p>
    </div>
  );
}

export function ApiEmptyState({ message }: { message: string }) {
  return (
    <div className="rounded-lg border border-border bg-surface-50 px-4 py-8 text-center text-sm text-text-muted">
      {message}
    </div>
  );
}

export function ApiLoadingState({ message = "Chargement…" }: { message?: string }) {
  return (
    <div className="rounded-lg border border-border bg-surface-50 px-4 py-8 text-center text-sm text-text-muted">
      {message}
    </div>
  );
}
