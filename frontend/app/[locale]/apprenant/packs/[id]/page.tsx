import { getTranslations, setRequestLocale } from "next-intl/server";
import { ContentCard } from "@/components/ui/content-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiErrorBox } from "@/components/ui/api-state";
import { getApprenantPack } from "@/lib/api/roles/apprenant";
import { requireRole } from "@/lib/auth/server";

type PageProps = { params: Promise<{ locale: string; id: string }> };

export default async function ApprenantPackDetailPage({ params }: PageProps) {
  const { locale, id } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("apprenantPages.packDetail");

  try {
    const { token } = await requireRole(locale, "apprenant");
    const pack = await getApprenantPack(token, id);

    return (
      <>
        <PageHeader title={pack.title} description={t("description")} variant="highlight" />
        <ContentCard accent="highlight">
          <p className="text-sm text-text-muted">{pack.description}</p>
          <p className="mt-4 text-sm">{pack.priceDzd} DZD · {pack.durationDays} jours</p>
          <p className="text-sm">Max projets : {pack.maxProjects}</p>
          <ul className="mt-4 list-disc space-y-1 pl-5 text-sm text-text-muted">
            {pack.features.map((f) => (
              <li key={f}>{f}</li>
            ))}
          </ul>
        </ContentCard>
      </>
    );
  } catch (error) {
    return <ApiErrorBox error={error} />;
  }
}
