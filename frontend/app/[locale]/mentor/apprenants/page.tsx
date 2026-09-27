import { getTranslations, setRequestLocale } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { EntityCard } from "@/components/data/entity-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiEmptyState, ApiErrorBox } from "@/components/ui/api-state";
import { getMentorApprenants } from "@/lib/api/roles/mentor";
import { requireRole } from "@/lib/auth/server";

type PageProps = { params: Promise<{ locale: string }> };

export default async function MentorApprenantsPage({ params }: PageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("mentorPages.apprenants");

  try {
    const { token } = await requireRole(locale, "mentor");
    const apprenants = await getMentorApprenants(token);

    return (
      <>
        <PageHeader title={t("title")} description={t("description")} variant="accent" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {apprenants.length === 0 ? (
            <ApiEmptyState message="Aucun apprenant associé." />
          ) : (
            apprenants.map((apprenant) => (
              <Link key={apprenant.id} href={`/apprenants/${apprenant.id}`}>
                <EntityCard
                  title={apprenant.displayName}
                  meta={`Score : ${apprenant.score}`}
                  accent="accent"
                />
              </Link>
            ))
          )}
        </div>
      </>
    );
  } catch (error) {
    return <ApiErrorBox error={error} />;
  }
}
