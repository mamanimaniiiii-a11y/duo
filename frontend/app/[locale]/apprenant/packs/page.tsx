import { getTranslations, setRequestLocale } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { EntityCard } from "@/components/data/entity-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiEmptyState, ApiErrorBox } from "@/components/ui/api-state";
import {
  getApprenantPackPurchases,
  getApprenantPacks,
} from "@/lib/api/roles/apprenant";
import { requireRole } from "@/lib/auth/server";

type PageProps = { params: Promise<{ locale: string }> };

export default async function ApprenantPacksPage({ params }: PageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("apprenantPages.packs");

  try {
    const { token } = await requireRole(locale, "apprenant");
    const [packs, purchases] = await Promise.all([
      getApprenantPacks(token),
      getApprenantPackPurchases(token),
    ]);

    return (
      <>
        <PageHeader title={t("title")} description={t("description")} variant="highlight" />
        <h2 className="mb-4 text-lg font-semibold">Packs disponibles</h2>
        <div className="mb-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {packs.length === 0 ? (
            <ApiEmptyState message="Aucun pack disponible." />
          ) : (
            packs.map((pack) => (
              <Link key={pack.id} href={`/apprenant/packs/${pack.id}`}>
                <EntityCard
                  title={pack.title}
                  description={pack.description}
                  meta={`${pack.priceDzd} DZD`}
                  accent="highlight"
                />
              </Link>
            ))
          )}
        </div>
        <h2 className="mb-4 text-lg font-semibold">Mes achats</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {purchases.length === 0 ? (
            <ApiEmptyState message="Aucun achat de pack." />
          ) : (
            purchases.map((purchase) => (
              <EntityCard
                key={purchase.id}
                title={`Pack ${purchase.packId}`}
                meta={`${purchase.status} · ${purchase.amountDzd} DZD`}
                accent="primary"
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
