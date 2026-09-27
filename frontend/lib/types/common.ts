/** Texte affiché selon la langue de l'interface */
export interface LocalizedString {
  fr: string;
  en: string;
  ar: string;
}

export type Locale = "fr" | "en" | "ar";

export type UserRole = "client" | "mentor" | "apprenant" | "admin";

/** Score de réputation, toujours borné 0–100 */
export type Score = number;

export type ProjectStatus =
  | "draft"
  | "published"
  | "assigned"
  | "in_progress"
  | "delivered"
  | "completed"
  | "cancelled";

export type TaskStatus =
  | "todo"
  | "in_progress"
  | "submitted"
  | "revision"
  | "approved";

export type DeliverableStatus =
  | "pending"
  | "submitted"
  | "revision_requested"
  | "approved";

export type PackPurchaseStatus =
  | "pending_payment"
  | "pending_admin"
  | "active"
  | "expired"
  | "cancelled";

export type BoostStatus =
  | "inactive"
  | "pending_payment"
  | "active"
  | "expired";
