import { getTranslations, setRequestLocale } from "next-intl/server";
import { ContentCard } from "@/components/ui/content-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiErrorBox } from "@/components/ui/api-state";
import { getMentorProgression } from "@/lib/api/roles/mentor";
import { requireRole } from "@/lib/auth/server";

type PageProps = { params: Promise<{ locale: string }> };

export default async function MentorProgressionPage({ params }: PageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("mentorPages.progression");

  try {
    const { token } = await requireRole(locale, "mentor");
    const score = await getMentorProgression(token);

    return (
      <>
        <PageHeader title={t("title")} description={t("description")} variant="accent" />
        <ContentCard accent="accent">
          <p className="text-3xl font-semibold text-text-primary">{score.total}</p>
          <p className="mt-2 text-sm text-text-muted">Score total</p>
          <p className="mt-4 text-sm">Projets complétés : {score.projectsCompleted}</p>
          {score.apprenticesMentored != null && (
            <p className="text-sm">Apprenants encadrés : {score.apprenticesMentored}</p>
          )}
          <p className="text-sm">Note moyenne : {score.averageRating}</p>
        </ContentCard>
      </>
    );
  } catch (error) {
    return <ApiErrorBox error={error} />;
  }
}
