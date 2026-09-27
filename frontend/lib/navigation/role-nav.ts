import type { UserRole } from "@/lib/types";

export type NavItem = {
  href: string;
  labelKey: string;
};

export const ROLE_NAV: Record<UserRole, NavItem[]> = {
  client: [
    { href: "/client/dashboard", labelKey: "nav.dashboard" },
    { href: "/client/projets", labelKey: "nav.projects" },
    { href: "/account", labelKey: "nav.account" },
    { href: "/messages", labelKey: "nav.messages" },
    { href: "/notifications", labelKey: "nav.notifications" },
  ],
  mentor: [
    { href: "/mentor/dashboard", labelKey: "nav.dashboard" },
    { href: "/mentor/projets", labelKey: "nav.projects" },
    { href: "/mentor/recrutement", labelKey: "nav.recruitment" },
    { href: "/mentor/apprenants", labelKey: "nav.apprenants" },
    { href: "/mentor/packs", labelKey: "nav.packs" },
    { href: "/mentor/boost", labelKey: "nav.boost" },
    { href: "/mentor/progression", labelKey: "nav.progression" },
    { href: "/account", labelKey: "nav.account" },
  ],
  apprenant: [
    { href: "/apprenant/dashboard", labelKey: "nav.dashboard" },
    { href: "/apprenant/decouvrir", labelKey: "nav.discover" },
    { href: "/apprenant/activite", labelKey: "nav.activity" },
    { href: "/apprenant/packs", labelKey: "nav.packs" },
    { href: "/apprenant/progression", labelKey: "nav.progression" },
    { href: "/apprenant/profil", labelKey: "nav.profile" },
    { href: "/account", labelKey: "nav.account" },
  ],
  admin: [
    { href: "/admin/dashboard", labelKey: "nav.dashboard" },
    { href: "/admin/utilisateurs", labelKey: "nav.users" },
    { href: "/admin/moderation", labelKey: "nav.moderation" },
    { href: "/admin/litiges", labelKey: "nav.disputes" },
    { href: "/admin/configuration", labelKey: "nav.configuration" },
    { href: "/admin/boost-premium", labelKey: "nav.boostPremium" },
  ],
};

export const ROLE_SHELL_STYLES: Record<
  UserRole,
  { sidebar: string; sidebarActive: string; badge: string }
> = {
  client: {
    sidebar: "bg-primary-600",
    sidebarActive: "bg-primary-800",
    badge: "bg-primary-800",
  },
  mentor: {
    sidebar: "bg-primary-600",
    sidebarActive: "bg-primary-800",
    badge: "bg-primary-800",
  },
  apprenant: {
    sidebar: "bg-primary-600",
    sidebarActive: "bg-primary-800",
    badge: "bg-primary-800",
  },
  admin: {
    sidebar: "bg-primary-800",
    sidebarActive: "bg-primary-600",
    badge: "bg-primary-600",
  },
};
