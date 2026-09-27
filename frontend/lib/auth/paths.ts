import type { UserRole } from "@/lib/types/common";

export function roleDashboardPath(role: UserRole): string {
  switch (role) {
    case "client":
      return "/client/dashboard";
    case "mentor":
      return "/mentor/dashboard";
    case "apprenant":
      return "/apprenant/dashboard";
    case "admin":
      return "/admin/dashboard";
  }
}

export function roleOnboardingPath(role: UserRole): string {
  switch (role) {
    case "client":
      return "/client/onboarding";
    case "mentor":
      return "/mentor/onboarding";
    case "apprenant":
      return "/apprenant/onboarding";
    case "admin":
      return "/admin/dashboard";
  }
}

export function getPostAuthPath(role: UserRole, onboardingCompleted: boolean): string {
  if (onboardingCompleted) {
    return roleDashboardPath(role);
  }
  return roleOnboardingPath(role);
}