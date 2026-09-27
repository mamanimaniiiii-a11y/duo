import type { Score } from "./common";
import type { Task } from "./task";

export interface MentorSuggestion {
  mentorId: string;
  score: Score;
  justification: string;
}

export interface AiTaskBreakdown {
  suggestedTasks: Omit<
    Task,
    "id" | "projectId" | "status" | "assignedApprenantId"
  >[];
}

export interface AiReviewReport {
  completeness: Score;
  qualityNotes: string[];
  meetsCriteria: boolean;
  summary: string;
}

export interface AiGapRecommendation {
  skillGap: string;
  recommendedProjectIds: string[];
  explanation: string;
}
