import { getTranslations, setRequestLocale } from "next-intl/server";
import { EntityCard } from "@/components/data/entity-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiEmptyState, ApiErrorBox } from "@/components/ui/api-state";
import { getApprenantListings } from "@/lib/api/roles/apprenant";
import { requireRole } from "@/lib/auth/server";

type PageProps = { params: Promise<{ locale: string }> };

export default async function ApprenantDiscoverPage({ params }: PageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("apprenantPages.discover");

  try {
    const { token } = await requireRole(locale, "apprenant");
    const listings = await getApprenantListings(token);

    return (
      <>
        <PageHeader title={t("title")} description={t("description")} variant="highlight" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {listings.length === 0 ? (
            <ApiEmptyState message="Aucune annonce à découvrir." />
          ) : (
            listings.map((listing) => (
              <EntityCard
                key={listing.id}
                href={`/annonces/${listing.id}`}
                title={listing.title}
                description={listing.description}
                meta={listing.requiredSkills.join(", ")}
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
