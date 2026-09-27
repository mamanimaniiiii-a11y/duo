import { getTranslations, setRequestLocale } from "next-intl/server";
import { ContentCard } from "@/components/ui/content-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiErrorBox } from "@/components/ui/api-state";
import { getApprenantMission } from "@/lib/api/roles/apprenant";
import { requireRole } from "@/lib/auth/server";

type PageProps = { params: Promise<{ locale: string; id: string }> };

export default async function ApprenantMissionPage({ params }: PageProps) {
  const { locale, id } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("apprenantPages.mission");

  try {
    const { token } = await requireRole(locale, "apprenant");
    const mission = await getApprenantMission(token, id);

    return (
      <>
        <PageHeader title={mission.projectTitle} description={t("description")} variant="highlight" />
        <div className="grid gap-4 lg:grid-cols-2">
          <ContentCard accent="highlight">
            <p className="text-sm text-text-muted">{mission.projectDescription}</p>
            <p className="mt-4 text-sm">Progression projet : {mission.projectProgressPercent}%</p>
          </ContentCard>
          <ContentCard accent="primary">
            <h2 className="font-semibold text-primary-600">Ma tâche</h2>
            <p className="mt-2 font-medium text-text-primary">{mission.myTask.title}</p>
            <p className="mt-2 text-sm text-text-muted">{mission.myTask.description}</p>
            <p className="mt-2 text-sm">Statut : {mission.myTask.status}</p>
          </ContentCard>
          <ContentCard accent="accent">
            <h2 className="font-semibold text-primary-600">Critères d&apos;acceptation</h2>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-text-muted">
              {mission.acceptanceCriteria.map((c) => (
                <li key={c}>{c}</li>
              ))}
            </ul>
          </ContentCard>
        </div>
      </>
    );
  } catch (error) {
    return <ApiErrorBox error={error} />;
  }
}
