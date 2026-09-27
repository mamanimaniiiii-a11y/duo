import type { Score } from "./common";

export type ApplicationStatus =
  | "pending"
  | "accepted"
  | "rejected"
  | "withdrawn";

export interface Application {
  id: string;
  annonceId: string;
  apprenantId: string;
  status: ApplicationStatus;
  coverLetter: string;
  aiMatchScore?: Score;
  createdAt: string;
  updatedAt: string;
}
