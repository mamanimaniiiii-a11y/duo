import { getTranslations, setRequestLocale } from "next-intl/server";
import { RoleDashboardView } from "@/components/dashboard/role-dashboard-view";
import { ApiErrorBox } from "@/components/ui/api-state";
import { getMentorDashboard } from "@/lib/api/roles/mentor";
import { requireRole } from "@/lib/auth/server";

type PageProps = { params: Promise<{ locale: string }> };

export default async function MentorDashboardPage({ params }: PageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("mentor.dashboard");

  try {
    const { token } = await requireRole(locale, "mentor");
    const stats = await getMentorDashboard(token);

    return (
      <RoleDashboardView
        title={t("title")}
        description={t("description")}
        variant="accent"
        stats={[
          { label: "Projets actifs", value: stats.activeProjects, accent: "accent" },
          { label: "Annonces ouvertes", value: stats.openListings, accent: "primary" },
          { label: "Candidatures", value: stats.pendingApplications, accent: "highlight" },
          { label: "Score", value: stats.scoreBreakdown?.total ?? 0, accent: "primary" },
        ]}
        actions={[
          { href: "/mentor/projets", label: "Mes projets" },
          { href: "/mentor/recrutement", label: "Recrutement" },
          { href: "/mentor/apprenants", label: "Mes apprenants" },
          { href: "/mentor/profil", label: "Mon profil" },
        ]}
      />
    );
  } catch (error) {
    return <ApiErrorBox error={error} />;
  }
}
