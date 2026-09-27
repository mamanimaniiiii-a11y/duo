import { fetchApi } from "@/lib/api/client";
import { toTask } from "@/lib/api/mappers";
import type { Task } from "@/lib/types/task";

export type SuggestedTaskDraft = {
  title: string;
  description: string;
  acceptanceCriteria: string[];
  dueDate?: string | null;
  sortOrder: number;
};

function toSuggestedTaskDraft(record: Record<string, unknown>): SuggestedTaskDraft {
  return {
    title: String(record.title),
    description: String(record.description),
    acceptanceCriteria: (record.acceptance_criteria as string[]) ?? [],
    dueDate: record.due_date ? String(record.due_date) : null,
    sortOrder: Number(record.sort_order ?? 0),
  };
}

export async function previewTaskBreakdown(
  token: string,
  projectId: string,
  taskCount: number,
): Promise<SuggestedTaskDraft[]> {
  const record = await fetchApi<Record<string, unknown>>(
    `/ai/projects/${projectId}/task-breakdown?task_count=${taskCount}`,
    { method: "POST", token },
  );
  const tasks = (record.suggested_tasks as Record<string, unknown>[]) ?? [];
  return tasks.map(toSuggestedTaskDraft);
}

export async function applyTaskBreakdown(
  token: string,
  projectId: string,
  suggestedTasks: SuggestedTaskDraft[],
): Promise<Task[]> {
  const records = await fetchApi<Record<string, unknown>[]>(
    `/ai/projects/${projectId}/task-breakdown/apply`,
    {
      method: "POST",
      token,
      body: {
        suggested_tasks: suggestedTasks.map((task) => ({
          title: task.title,
          description: task.description,
          acceptance_criteria: task.acceptanceCriteria,
          due_date: task.dueDate ?? null,
          sort_order: task.sortOrder,
        })),
      },
    },
  );
  return records.map(toTask);
}
