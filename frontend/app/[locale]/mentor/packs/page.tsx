import { getTranslations, setRequestLocale } from "next-intl/server";
import { EntityCard } from "@/components/data/entity-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiEmptyState, ApiErrorBox } from "@/components/ui/api-state";
import { getMentorPacks } from "@/lib/api/roles/mentor";
import { requireRole } from "@/lib/auth/server";

type PageProps = { params: Promise<{ locale: string }> };

export default async function MentorPacksPage({ params }: PageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("mentorPages.packs");

  try {
    const { token } = await requireRole(locale, "mentor");
    const packs = await getMentorPacks(token);

    return (
      <>
        <PageHeader title={t("title")} description={t("description")} variant="accent" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {packs.length === 0 ? (
            <ApiEmptyState message="Aucun pack créé." />
          ) : (
            packs.map((pack) => (
              <EntityCard
                key={pack.id}
                title={pack.title}
                description={pack.description}
                meta={`${pack.priceDzd} DZD · ${pack.durationDays} jours`}
                accent="accent"
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
