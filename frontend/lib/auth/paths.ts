import type { UserRole } from "@/lib/types/common";

export function getDashboardPath(role: UserRole): string {
  switch (role) {
    case "client":
      return "/client/dashboard";
    case "mentor":
      return "/mentor/dashboard";
    case "apprenant":
      return "/apprenant/dashboard";
    case "admin":
      return "/admin/dashboard";
    default:
      return "/";
  }
}

export function getOnboardingPath(role: UserRole): string {
  switch (role) {
    case "client":
      return "/client/onboarding";
    case "mentor":
      return "/mentor/onboarding";
    case "apprenant":
      return "/apprenant/onboarding";
    default:
      return getDashboardPath(role);
  }
}

export function getPostAuthPath(
  role: UserRole,
  onboardingCompleted: boolean,
): string {
  if (!onboardingCompleted && role !== "admin") {
    return getOnboardingPath(role);
  }
  return getDashboardPath(role);
}
