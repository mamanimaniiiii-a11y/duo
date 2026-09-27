import type { LocalizedString } from "./common";

export interface Category {
  id: string;
  slug: string;
  name: LocalizedString;
  isActive: boolean;
  sortOrder: number;
}
