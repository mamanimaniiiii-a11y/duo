import type { TaskStatus } from "./common";

export interface Task {
  id: string;
  projectId: string;
  title: string;
  description: string;
  status: TaskStatus;
  assignedApprenantId?: string;
  acceptanceCriteria: string[];
  dueDate?: string;
  sortOrder: number;
}

export interface Submission {
  id: string;
  taskId: string;
  contentUrl?: string;
  fileIds: string[];
  submittedAt: string;
  mentorFeedback?: string;
}
