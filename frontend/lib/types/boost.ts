import type { LocalizedString } from "./common";

export interface BoostOption {
  id: string;
  label: LocalizedString;
  durationDays: number;
  priceDzd: number;
  isActive: boolean;
}

export interface PremiumPlan {
  id: string;
  label: LocalizedString;
  priceDzd: number;
  durationDays: number;
  benefits: string[];
  isActive: boolean;
}
