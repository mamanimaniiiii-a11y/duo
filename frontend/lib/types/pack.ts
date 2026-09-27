import type { PackPurchaseStatus } from "./common";

export interface MentorPack {
  id: string;
  mentorId: string;
  projectId?: string;
  title: string;
  description: string;
  priceDzd: number;
  durationDays: number;
  maxProjects: number;
  features: string[];
  isActive: boolean;
}

export interface PackPurchase {
  id: string;
  packId: string;
  apprenantId: string;
  mentorId: string;
  status: PackPurchaseStatus;
  purchasedAt?: string;
  expiresAt?: string;
  amountDzd: number;
}
