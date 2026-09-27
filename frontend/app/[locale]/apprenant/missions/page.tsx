import { getTranslations, setRequestLocale } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { ContentCard } from "@/components/ui/content-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiErrorBox } from "@/components/ui/api-state";
import { getApprenantMissions } from "@/lib/api/roles/apprenant";
import { requireRole } from "@/lib/auth/server";

type PageProps = { params: Promise<{ locale: string }> };

export default async function ApprenantMissionsPage({ params }: PageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("apprenantPages.missions");

  try {
    const { token } = await requireRole(locale, "apprenant");
    const missions = await getApprenantMissions(token);

    return (
      <>
        <PageHeader title={t("title")} description={t("description")} variant="highlight" />
        <ContentCard accent="highlight">
          {missions.length === 0 ? (
            <p className="text-sm text-text-muted">Aucune mission assignée pour le moment.</p>
          ) : (
            <ul className="divide-y divide-border">
              {missions.map((mission) => (
                <li key={mission.id} className="flex flex-col gap-2 py-4 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="font-medium text-text-primary">{mission.projectTitle}</p>
                    <p className="text-sm text-text-muted">{mission.myTask.title}</p>
                    <p className="mt-1 text-xs text-text-muted">
                      Progression projet : {mission.projectProgressPercent}%
                    </p>
                  </div>
                  <Link
                    href={`/apprenant/missions/${mission.id}`}
                    className="text-sm font-medium text-highlight-500 hover:underline"
                  >
                    Voir la mission
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </ContentCard>
      </>
    );
  } catch (error) {
    return <ApiErrorBox error={error} />;
  }
}
