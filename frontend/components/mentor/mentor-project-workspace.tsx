"use client";

import { useState } from "react";
import { useRouter } from "@/i18n/navigation";
import { Link } from "@/i18n/navigation";
import { ContentCard } from "@/components/ui/content-card";
import { FormField, formControlClass } from "@/components/ui/form-field";
import { PageContainer } from "@/components/ui/page-container";
import { getApiErrorMessage } from "@/lib/api/errors";
import { MentorAiTaskBreakdown } from "@/components/mentor/mentor-ai-task-breakdown";
import { TaskAssignApprenant } from "@/components/mentor/task-assign-apprenant";
import { createMentorPack, createMentorTask } from "@/lib/api/roles/mentor";
import { getClientAccessToken } from "@/lib/auth/client-storage";
import type { MentorPack } from "@/lib/types/pack";
import type { MentorProjectDetail } from "@/lib/types/project";
import type { ApprenantSummary } from "@/lib/types/user";

type MentorProjectWorkspaceProps = {
  project: MentorProjectDetail;
  eligibleApprenants: ApprenantSummary[];
  assignableApprenants: ApprenantSummary[];
  packs: MentorPack[];
};

function parseLines(raw: string): string[] {
  return raw
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
}

export function MentorProjectWorkspace({
  project,
  eligibleApprenants,
  assignableApprenants,
  packs: initialPacks,
}: MentorProjectWorkspaceProps) {
  const router = useRouter();
  const [packs, setPacks] = useState(initialPacks);
  const [error, setError] = useState<string | null>(null);
  const [taskLoading, setTaskLoading] = useState(false);
  const [packLoading, setPackLoading] = useState(false);

  const [taskTitle, setTaskTitle] = useState("");
  const [taskDescription, setTaskDescription] = useState("");
  const [taskCriteria, setTaskCriteria] = useState("");

  const [packTitle, setPackTitle] = useState("");
  const [packDescription, setPackDescription] = useState("");
  const [packPrice, setPackPrice] = useState("");
  const [packDuration, setPackDuration] = useState("30");
  const [packMaxProjects, setPackMaxProjects] = useState("1");

  const apprenantById = new Map(
    [...assignableApprenants, ...eligibleApprenants, ...project.assignedApprenants].map(
      (a) => [a.id, a],
    ),
  );

  const canUseAiBreakdown =
    project.status === "assigned" || project.status === "in_progress";

  async function handleCreateTask(event: React.FormEvent) {
    event.preventDefault();
    const token = getClientAccessToken();
    if (!token) return;

    setError(null);
    setTaskLoading(true);
    try {
      await createMentorTask(token, project.id, {
        title: taskTitle.trim(),
        description: taskDescription.trim(),
        acceptanceCriteria: parseLines(taskCriteria),
      });
      setTaskTitle("");
      setTaskDescription("");
      setTaskCriteria("");
      router.refresh();
    } catch (err) {
      setError(getApiErrorMessage(err, "register"));
    } finally {
      setTaskLoading(false);
    }
  }

  async function handleCreatePack(event: React.FormEvent) {
    event.preventDefault();
    const token = getClientAccessToken();
    if (!token) return;

    setError(null);
    setPackLoading(true);
    try {
      const created = await createMentorPack(token, {
        title: packTitle.trim(),
        description: packDescription.trim(),
        priceDzd: Number(packPrice),
        durationDays: Number(packDuration),
        maxProjects: Number(packMaxProjects),
        projectId: project.id,
      });
      setPacks((current) => [...current, created]);
      setPackTitle("");
      setPackDescription("");
      setPackPrice("");
      setPackDuration("30");
      setPackMaxProjects("1");
      router.refresh();
    } catch (err) {
      setError(getApiErrorMessage(err, "register"));
    } finally {
      setPackLoading(false);
    }
  }

  return (
    <PageContainer>
      <div className="grid gap-6 lg:grid-cols-2">
        <ContentCard accent="primary" className="shadow-sm">
          <h2 className="font-semibold text-primary-600">Projet</h2>
          <p className="mt-2 text-sm leading-relaxed text-text-muted">{project.description}</p>
          <p className="mt-4 text-sm">Client : {project.client.displayName}</p>
          <p className="text-sm">Statut : {project.status}</p>
          <p className="text-sm">Progression : {project.progressPercent}%</p>
        </ContentCard>

        <ContentCard accent="primary" className="shadow-sm">
          <div className="flex items-center justify-between gap-3">
            <h2 className="font-semibold text-primary-600">Apprenants</h2>
            <Link
              href="/mentor/recrutement"
              className="text-sm font-medium text-primary-600 hover:underline"
            >
              Recruter
            </Link>
          </div>
          {eligibleApprenants.length === 0 ? (
            <p className="mt-3 text-sm text-text-muted">
              Aucun apprenant éligible. Publiez une annonce liée à ce projet et acceptez des
              candidatures depuis Recrutement.
            </p>
          ) : (
            <ul className="mt-3 divide-y divide-border text-sm">
              {eligibleApprenants.map((apprenant) => (
                <li key={apprenant.id} className="flex justify-between py-2">
                  <span className="font-medium text-text-primary">{apprenant.displayName}</span>
                  <span className="text-text-muted">Score {apprenant.score}</span>
                </li>
              ))}
            </ul>
          )}
          {project.assignedApprenants.length > 0 && (
            <p className="mt-3 text-xs text-text-muted">
              {project.assignedApprenants.length} apprenant(s) déjà assigné(s) à une tâche.
            </p>
          )}
        </ContentCard>

        <ContentCard accent="primary" className="shadow-sm lg:col-span-2">
          <h2 className="font-semibold text-primary-600">Tâches</h2>
          {assignableApprenants.length > 0 && (
            <p className="mt-2 text-xs text-text-muted">
              Apprenants disponibles pour assignation :{" "}
              {assignableApprenants.map((a) => `@${a.username}`).join(", ")}
            </p>
          )}

          {canUseAiBreakdown && (
            <div className="mt-4">
              <MentorAiTaskBreakdown
                projectId={project.id}
                learnerComplexityLevel={project.learnerComplexityLevel}
                existingTaskCount={project.tasks.length}
              />
            </div>
          )}

          {project.tasks.length === 0 ? (
            <p className="mt-2 text-sm text-text-muted">Aucune tâche pour ce projet.</p>
          ) : (
            <ul className="mt-4 space-y-3">
              {project.tasks.map((task) => (
                <li
                  key={task.id}
                  className="rounded-lg border border-border bg-surface-50 p-4"
                >
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                      <p className="font-medium text-text-primary">{task.title}</p>
                      {task.description && (
                        <p className="mt-1 text-sm text-text-muted">{task.description}</p>
                      )}
                      <p className="mt-1 text-xs text-text-muted">Statut : {task.status}</p>
                    </div>
                    <TaskAssignApprenant
                      projectId={project.id}
                      taskId={task.id}
                      assignableApprenants={assignableApprenants}
                      assignedApprenant={
                        task.assignedApprenantId
                          ? apprenantById.get(task.assignedApprenantId)
                          : undefined
                      }
                    />
                  </div>
                </li>
              ))}
            </ul>
          )}

          <form className="mt-6 grid gap-4 border-t border-border pt-6" onSubmit={handleCreateTask}>
            <h3 className="text-sm font-semibold text-text-primary">Ajouter une tâche</h3>
            <FormField label="Titre" htmlFor="taskTitle">
              <input
                id="taskTitle"
                required
                minLength={3}
                value={taskTitle}
                onChange={(e) => setTaskTitle(e.target.value)}
                className={formControlClass}
              />
            </FormField>
            <FormField label="Description" htmlFor="taskDescription">
              <textarea
                id="taskDescription"
                rows={2}
                value={taskDescription}
                onChange={(e) => setTaskDescription(e.target.value)}
                className={formControlClass}
              />
            </FormField>
            <FormField
              label="Critères d'acceptation"
              htmlFor="taskCriteria"
              hint="Un critère par ligne."
            >
              <textarea
                id="taskCriteria"
                rows={3}
                value={taskCriteria}
                onChange={(e) => setTaskCriteria(e.target.value)}
                className={formControlClass}
                placeholder="Livrable testé&#10;Documentation incluse"
              />
            </FormField>
            <button
              type="submit"
              disabled={taskLoading}
              className="w-fit rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-primary-800 disabled:opacity-60"
            >
              {taskLoading ? "…" : "Créer la tâche"}
            </button>
          </form>
        </ContentCard>

        <ContentCard accent="primary" className="shadow-sm lg:col-span-2">
          <h2 className="font-semibold text-primary-600">Packs liés au projet</h2>
          <p className="mt-1 text-sm text-text-muted">
            Offres que les apprenants peuvent acheter pour ce projet.
          </p>

          {packs.length === 0 ? (
            <p className="mt-3 text-sm text-text-muted">Aucun pack pour ce projet.</p>
          ) : (
            <ul className="mt-4 grid gap-3 sm:grid-cols-2">
              {packs.map((pack) => (
                <li key={pack.id} className="rounded-lg border border-border bg-surface-50 p-4">
                  <p className="font-medium text-text-primary">{pack.title}</p>
                  <p className="mt-1 text-sm text-text-muted line-clamp-2">{pack.description}</p>
                  <p className="mt-2 text-xs text-text-muted">
                    {pack.priceDzd} DZD · {pack.durationDays} jours · {pack.maxProjects} projet(s)
                  </p>
                </li>
              ))}
            </ul>
          )}

          <form className="mt-6 grid gap-4 border-t border-border pt-6 sm:grid-cols-2" onSubmit={handleCreatePack}>
            <h3 className="text-sm font-semibold text-text-primary sm:col-span-2">
              Créer un pack pour ce projet
            </h3>
            <FormField label="Titre" htmlFor="packTitle">
              <input
                id="packTitle"
                required
                minLength={3}
                value={packTitle}
                onChange={(e) => setPackTitle(e.target.value)}
                className={formControlClass}
              />
            </FormField>
            <FormField label="Prix (DZD)" htmlFor="packPrice">
              <input
                id="packPrice"
                type="number"
                required
                min={0}
                value={packPrice}
                onChange={(e) => setPackPrice(e.target.value)}
                className={formControlClass}
              />
            </FormField>
            <FormField label="Description" htmlFor="packDescription" hint="Minimum 10 caractères.">
              <textarea
                id="packDescription"
                required
                minLength={10}
                rows={3}
                value={packDescription}
                onChange={(e) => setPackDescription(e.target.value)}
                className={`${formControlClass} sm:col-span-2`}
              />
            </FormField>
            <FormField label="Durée (jours)" htmlFor="packDuration">
              <input
                id="packDuration"
                type="number"
                required
                min={1}
                value={packDuration}
                onChange={(e) => setPackDuration(e.target.value)}
                className={formControlClass}
              />
            </FormField>
            <FormField label="Nombre de projets inclus" htmlFor="packMaxProjects">
              <input
                id="packMaxProjects"
                type="number"
                required
                min={1}
                value={packMaxProjects}
                onChange={(e) => setPackMaxProjects(e.target.value)}
                className={formControlClass}
              />
            </FormField>
            <div className="sm:col-span-2">
              <button
                type="submit"
                disabled={packLoading}
                className="rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-primary-800 disabled:opacity-60"
              >
                {packLoading ? "…" : "Créer le pack"}
              </button>
            </div>
          </form>
        </ContentCard>
      </div>

      {error && (
        <p role="alert" className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </p>
      )}
    </PageContainer>
  );
}
