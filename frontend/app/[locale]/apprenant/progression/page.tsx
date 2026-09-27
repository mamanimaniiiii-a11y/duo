import { getTranslations, setRequestLocale } from "next-intl/server";
import { ContentCard } from "@/components/ui/content-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiErrorBox } from "@/components/ui/api-state";
import { getApprenantProgression } from "@/lib/api/roles/apprenant";
import { requireRole } from "@/lib/auth/server";

type PageProps = { params: Promise<{ locale: string }> };

export default async function ApprenantProgressionPage({ params }: PageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("apprenantPages.progression");

  try {
    const { token } = await requireRole(locale, "apprenant");
    const score = await getApprenantProgression(token);

    return (
      <>
        <PageHeader title={t("title")} description={t("description")} variant="highlight" />
        <ContentCard accent="highlight">
          <p className="text-3xl font-semibold text-text-primary">{score.total}</p>
          <p className="mt-2 text-sm text-text-muted">Score total</p>
          <p className="mt-4 text-sm">Projets complétés : {score.projectsCompleted}</p>
          <p className="text-sm">Note moyenne : {score.averageRating}</p>
        </ContentCard>
      </>
    );
  } catch (error) {
    return <ApiErrorBox error={error} />;
  }
}
