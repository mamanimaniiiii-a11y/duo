"use client";

import { useMemo, useState } from "react";
import { useRouter } from "@/i18n/navigation";
import { getApiErrorMessage } from "@/lib/api/errors";
import { updateMentorTask } from "@/lib/api/roles/mentor";
import { getClientAccessToken } from "@/lib/auth/client-storage";
import { formControlClass } from "@/components/ui/form-field";
import type { ApprenantSummary } from "@/lib/types/user";

type TaskAssignApprenantProps = {
  projectId: string;
  taskId: string;
  assignableApprenants: ApprenantSummary[];
  assignedApprenant?: ApprenantSummary;
};

export function TaskAssignApprenant({
  projectId,
  taskId,
  assignableApprenants,
  assignedApprenant,
}: TaskAssignApprenantProps) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [filter, setFilter] = useState("");
  const [assigning, setAssigning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const filtered = useMemo(() => {
    const query = filter.trim().toLowerCase();
    if (!query) return assignableApprenants;
    return assignableApprenants.filter(
      (apprenant) =>
        apprenant.username.toLowerCase().includes(query) ||
        apprenant.displayName.toLowerCase().includes(query),
    );
  }, [assignableApprenants, filter]);

  async function handleAssign(apprenantId: string) {
    const token = getClientAccessToken();
    if (!token) return;

    setError(null);
    setAssigning(true);
    try {
      await updateMentorTask(token, projectId, taskId, { assignedApprenantId: apprenantId });
      setOpen(false);
      setFilter("");
      router.refresh();
    } catch (err) {
      setError(getApiErrorMessage(err, "register"));
    } finally {
      setAssigning(false);
    }
  }

  return (
    <div className="min-w-[260px]">
      {assignedApprenant ? (
        <p className="mb-2 text-xs text-green-700">
          Assigné à <span className="font-semibold">@{assignedApprenant.username}</span>
        </p>
      ) : (
        <p className="mb-2 text-xs text-text-muted">Non assigné</p>
      )}

      <button
        type="button"
        onClick={() => setOpen((current) => !current)}
        className="rounded-lg border border-primary-200 bg-white px-3 py-2 text-xs font-semibold text-primary-700 hover:bg-primary-50"
      >
        {open ? "Fermer" : assignedApprenant ? "Changer l'apprenant" : "Assigner un apprenant"}
      </button>

      {open && (
        <div className="mt-2 rounded-lg border border-border bg-white p-3">
          <p className="mb-2 text-xs text-text-muted">
            Seuls les comptes avec le rôle apprenant sont acceptés.
          </p>
          <input
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Filtrer par username ou nom"
            className={formControlClass}
          />
          {filtered.length === 0 ? (
            <p className="mt-2 text-xs text-text-muted">Aucun apprenant trouvé.</p>
          ) : (
            <ul className="mt-2 max-h-40 space-y-1 overflow-y-auto text-sm">
              {filtered.map((apprenant) => (
                <li
                  key={apprenant.id}
                  className="flex items-center justify-between gap-2 rounded-md px-1 py-1 hover:bg-surface-50"
                >
                  <span>
                    <span className="font-medium">@{apprenant.username}</span>
                    <span className="text-text-muted"> · {apprenant.displayName}</span>
                  </span>
                  <button
                    type="button"
                    disabled={assigning}
                    onClick={() => handleAssign(apprenant.id)}
                    className="shrink-0 text-xs font-medium text-primary-600 hover:underline disabled:opacity-60"
                  >
                    Choisir
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  );
}
