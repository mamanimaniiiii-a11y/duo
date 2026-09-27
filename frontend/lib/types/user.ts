import type { BoostStatus, Locale, Score, UserRole } from "./common";

export interface User {
  id: string;
  email: string;
  role: UserRole;
  displayName: string;
  avatarUrl?: string;
  locale: Locale;
  onboardingCompleted: boolean;
  createdAt: string;
}

export interface MentorProfile {
  userId: string;
  bio: string;
  serviceCategoryIds: string[];
  score: Score;
  isCertified: boolean;
  isPremium: boolean;
  boostStatus: BoostStatus;
  boostExpiresAt?: string;
  availabilityNote?: string;
}

export interface ApprenantProfile {
  userId: string;
  skills: string[];
  careerGoal: string;
  score: Score;
  canBecomeFreelance: boolean;
  portfolioProjectIds: string[];
}

export interface ClientProfile {
  companyName?: string;
  phone?: string;
}

export interface ClientSummary {
  id: string;
  displayName: string;
  avatarUrl?: string;
}

export interface MentorSummary {
  id: string;
  displayName: string;
  avatarUrl?: string;
  score: Score;
  isCertified: boolean;
}

export interface ApprenantSummary {
  id: string;
  displayName: string;
  avatarUrl?: string;
  score: Score;
}
