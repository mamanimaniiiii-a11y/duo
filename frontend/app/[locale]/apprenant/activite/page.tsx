import { getTranslations, setRequestLocale } from "next-intl/server";
import { EntityCard } from "@/components/data/entity-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiEmptyState, ApiErrorBox } from "@/components/ui/api-state";
import { getApprenantApplications } from "@/lib/api/roles/apprenant";
import { requireRole } from "@/lib/auth/server";

type PageProps = { params: Promise<{ locale: string }> };

export default async function ApprenantActivityPage({ params }: PageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("apprenantPages.activity");

  try {
    const { token } = await requireRole(locale, "apprenant");
    const applications = await getApprenantApplications(token);

    return (
      <>
        <PageHeader title={t("title")} description={t("description")} variant="highlight" />
        <div className="grid gap-4 sm:grid-cols-2">
          {applications.length === 0 ? (
            <ApiEmptyState message="Aucune candidature." />
          ) : (
            applications.map((app) => (
              <EntityCard
                key={app.id}
                href={`/annonces/${app.annonceId}`}
                title={`Candidature · ${app.status}`}
                description={app.coverLetter}
                meta="Voir l'annonce"
                accent="highlight"
              />
            ))
          )}
        </div>
      </>
    );
  } catch (error) {
    return <ApiErrorBox error={error} />;
  }
}
