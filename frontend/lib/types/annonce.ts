export type AnnonceStatus = "draft" | "open" | "closed" | "archived";

export interface Annonce {
  id: string;
  mentorId: string;
  title: string;
  description: string;
  requiredSkills: string[];
  projectId?: string;
  status: AnnonceStatus;
  applicationsCount: number;
  createdAt: string;
  updatedAt: string;
}
