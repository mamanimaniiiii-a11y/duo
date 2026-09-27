"use client";

import { useState } from "react";
import { useRouter } from "@/i18n/navigation";
import { applyTaskBreakdown, previewTaskBreakdown, type SuggestedTaskDraft } from "@/lib/api/ai";
import { getApiErrorMessage } from "@/lib/api/errors";
import { getClientAccessToken } from "@/lib/auth/client-storage";
import { FormField, formControlClass } from "@/components/ui/form-field";

type MentorAiTaskBreakdownProps = {
  projectId: string;
  learnerComplexityLevel: string;
  existingTaskCount: number;
};

function parseCriteria(raw: string): string[] {
  return raw
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
}

export function MentorAiTaskBreakdown({
  projectId,
  learnerComplexityLevel,
  existingTaskCount,
}: MentorAiTaskBreakdownProps) {
  const router = useRouter();
  const [taskCount, setTaskCount] = useState(5);
  const [tasks, setTasks] = useState<SuggestedTaskDraft[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [applying, setApplying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function handleGenerate() {
    const token = getClientAccessToken();
    if (!token) return;

    setError(null);
    setSuccess(null);
    setLoading(true);
    try {
      const preview = await previewTaskBreakdown(token, projectId, taskCount);
      setTasks(preview);
    } catch (err) {
      setError(getApiErrorMessage(err, "register"));
    } finally {
      setLoading(false);
    }
  }

  async function handleApply() {
    const token = getClientAccessToken();
    if (!token || !tasks?.length) return;

    setError(null);
    setSuccess(null);
    setApplying(true);
    try {
      await applyTaskBreakdown(token, projectId, tasks);
      setSuccess("Tâches créées. Vous pouvez maintenant les assigner aux apprenants.");
      setTasks(null);
      router.refresh();
    } catch (err) {
      setError(getApiErrorMessage(err, "register"));
    } finally {
      setApplying(false);
    }
  }

  function updateTask(index: number, patch: Partial<SuggestedTaskDraft>) {
    setTasks((current) =>
      current
        ? current.map((task, i) => (i === index ? { ...task, ...patch } : task))
        : current,
    );
  }

  if (existingTaskCount > 0) {
    return (
      <div className="rounded-lg border border-border bg-surface-50 p-4">
        <h3 className="text-sm font-semibold text-text-primary">Tâches enregistrées</h3>
        <p className="mt-1 text-xs text-text-muted">
          {existingTaskCount} tâche(s) déjà sauvegardée(s) pour ce projet. Elles restent en base
          après rechargement. Assignez-les aux apprenants ci-dessous.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-border bg-surface-50 p-4">
      <h3 className="text-sm font-semibold text-text-primary">Générer les tâches avec l&apos;IA</h3>
      <p className="mt-1 text-xs text-text-muted">
        L&apos;IA propose, vous validez. Niveau client : {learnerComplexityLevel}.
      </p>

      <div className="mt-4 flex flex-wrap items-end gap-3">
        <FormField label="Nombre de tâches" htmlFor="ai-task-count">
          <input
            id="ai-task-count"
            type="number"
            min={3}
            max={8}
            value={taskCount}
            onChange={(e) => setTaskCount(Number(e.target.value))}
            className={`${formControlClass} w-24`}
          />
        </FormField>
        <button
          type="button"
          disabled={loading}
          onClick={handleGenerate}
          className="rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-primary-800 disabled:opacity-60"
        >
          {loading ? "Génération…" : "Générer les tâches avec l'IA"}
        </button>
      </div>

      {tasks && (
        <div className="mt-6 space-y-4">
          <p className="text-sm font-medium text-text-primary">Relecture et édition</p>
          {tasks.map((task, index) => (
            <div key={index} className="rounded-lg border border-border bg-white p-4">
              <p className="mb-2 text-xs font-medium text-text-muted">Tâche {index + 1}</p>
              <FormField label="Titre" htmlFor={`ai-task-title-${index}`}>
                <input
                  id={`ai-task-title-${index}`}
                  value={task.title}
                  onChange={(e) => updateTask(index, { title: e.target.value })}
                  className={formControlClass}
                />
              </FormField>
              <FormField label="Description" htmlFor={`ai-task-desc-${index}`}>
                <textarea
                  id={`ai-task-desc-${index}`}
                  rows={3}
                  value={task.description}
                  onChange={(e) => updateTask(index, { description: e.target.value })}
                  className={formControlClass}
                />
              </FormField>
              <FormField
                label="Critères d'acceptation"
                htmlFor={`ai-task-criteria-${index}`}
                hint="Un critère par ligne."
              >
                <textarea
                  id={`ai-task-criteria-${index}`}
                  rows={4}
                  value={task.acceptanceCriteria.join("\n")}
                  onChange={(e) =>
                    updateTask(index, { acceptanceCriteria: parseCriteria(e.target.value) })
                  }
                  className={formControlClass}
                />
              </FormField>
            </div>
          ))}
          <button
            type="button"
            disabled={applying}
            onClick={handleApply}
            className="rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-primary-800 disabled:opacity-60"
          >
            {applying ? "Enregistrement…" : "Valider et créer les tâches"}
          </button>
        </div>
      )}

      {error && (
        <p role="alert" className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </p>
      )}
      {success && (
        <p className="mt-3 rounded-lg bg-green-50 px-3 py-2 text-sm text-green-800">{success}</p>
      )}
    </div>
  );
}
