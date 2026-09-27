import type { Locale, UserRole } from "./common";
import type { ScoreBreakdown } from "./review";
import type { ApprenantProfile, ClientProfile, MentorProfile } from "./user";

export interface Account {
  id: string;
  email: string;
  username: string;
  role: UserRole;
  displayName: string;
  avatarUrl?: string;
  locale: Locale;
  onboardingCompleted: boolean;
  clientProfile?: ClientProfile;
  mentorProfile?: MentorProfile;
  apprenantProfile?: ApprenantProfile;
  scoreBreakdown?: ScoreBreakdown;
}
