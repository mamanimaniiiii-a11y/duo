import { getTranslations, setRequestLocale } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { EntityCard } from "@/components/data/entity-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiEmptyState, ApiErrorBox } from "@/components/ui/api-state";
import { getMentorListings } from "@/lib/api/roles/mentor";
import { requireRole } from "@/lib/auth/server";

type PageProps = { params: Promise<{ locale: string }> };

export default async function MentorRecruitmentPage({ params }: PageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("mentorPages.recruitment");

  try {
    const { token } = await requireRole(locale, "mentor");
    const listings = await getMentorListings(token);

    return (
      <>
        <PageHeader title={t("title")} description={t("description")} variant="accent" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {listings.length === 0 ? (
            <ApiEmptyState message="Aucune annonce de recrutement." />
          ) : (
            listings.map((listing) => (
              <Link key={listing.id} href={`/annonces/${listing.id}`}>
                <EntityCard
                  title={listing.title}
                  description={listing.description}
                  meta={`${listing.status} · ${listing.applicationsCount} candidature(s)`}
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
