import { getTranslations, setRequestLocale } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { RoleDashboardView } from "@/components/dashboard/role-dashboard-view";
import { ApiErrorBox } from "@/components/ui/api-state";
import { getApprenantDashboard, getApprenantMissions } from "@/lib/api/roles/apprenant";
import { requireRole } from "@/lib/auth/server";

type PageProps = { params: Promise<{ locale: string }> };

export default async function ApprenantDashboardPage({ params }: PageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("apprenant.dashboard");

  try {
    const { token } = await requireRole(locale, "apprenant");
    const [stats, missions] = await Promise.all([
      getApprenantDashboard(token),
      getApprenantMissions(token),
    ]);

    return (
      <RoleDashboardView
        title={t("title")}
        description={t("description")}
        variant="highlight"
        stats={[
          { label: "Missions", value: stats.activeProjects, accent: "highlight" },
          { label: "Candidatures", value: stats.pendingApplications, accent: "primary" },
          { label: "Packs actifs", value: stats.activePacks, accent: "accent" },
          { label: "Score", value: stats.scoreBreakdown?.total ?? 0, accent: "primary" },
        ]}
        actions={[
          { href: "/apprenant/decouvrir", label: "Découvrir les annonces" },
          { href: "/apprenant/activite", label: "Mon activité" },
          { href: "/apprenant/packs", label: "Packs mentor" },
          { href: "/apprenant/profil", label: "Mon profil" },
        ]}
        sectionTitle="Missions en cours"
        sectionContent={
          missions.length === 0 ? (
            <p className="text-sm text-text-muted">Aucune mission assignée pour le moment.</p>
          ) : (
            <ul className="divide-y divide-border">
              {missions.slice(0, 5).map((mission) => (
                <li key={mission.id} className="flex items-center justify-between py-3">
                  <div>
                    <p className="font-medium text-text-primary">{mission.projectTitle}</p>
                    <p className="text-sm text-text-muted">{mission.myTask.title}</p>
                  </div>
                  <Link
                    href={`/apprenant/missions/${mission.id}`}
                    className="text-sm font-medium text-highlight-500 hover:underline"
                  >
                    Ouvrir
                  </Link>
                </li>
              ))}
            </ul>
          )
        }
      />
    );
  } catch (error) {
    return <ApiErrorBox error={error} />;
  }
}
