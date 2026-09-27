import type { ProjectStatus } from "./common";
import type { Deliverable } from "./deliverable";
import type { Task } from "./task";
import type { Submission } from "./task";
import type { AiReviewReport, MentorSuggestion } from "./ai";
import type {
  ApprenantSummary,
  ClientSummary,
  MentorSummary,
} from "./user";

/** Vue CLIENT — pas de tâches internes */
export interface ClientProjectDetail {
  id: string;
  title: string;
  description: string;
  categoryId: string;
  status: ProjectStatus;
  budgetDzd?: number;
  deadline?: string;
  progressPercent: number;
  mentor?: MentorSummary;
  deliverables: Deliverable[];
  aiMentorSuggestions?: MentorSuggestion[];
}

/** Vue MENTOR — accès complet aux sous-tâches */
export interface MentorProjectDetail {
  id: string;
  title: string;
  description: string;
  categoryId: string;
  status: ProjectStatus;
  client: ClientSummary;
  progressPercent: number;
  tasks: Task[];
  deliverables: Deliverable[];
  assignedApprenants: ApprenantSummary[];
}

/** Vue APPRENANT — contexte projet sans tâches des autres */
export interface ApprenantMissionDetail {
  id: string;
  projectId: string;
  projectTitle: string;
  projectDescription: string;
  projectProgressPercent: number;
  projectExpectedDeliverables: string[];
  myTask: Task;
  acceptanceCriteria: string[];
  submissions: Submission[];
  aiReviewReport?: AiReviewReport;
}
