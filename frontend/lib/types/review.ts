import type { Score } from "./common";

export type ReviewType =
  | "client_to_mentor"
  | "mentor_to_apprenant"
  | "apprenant_to_mentor";

export interface Review {
  id: string;
  fromUserId: string;
  toUserId: string;
  projectId?: string;
  rating: number;
  comment: string;
  type: ReviewType;
  createdAt: string;
}

export interface ScoreBreakdown {
  total: Score;
  projectsCompleted: number;
  apprenticesMentored?: number;
  averageRating: number;
}
