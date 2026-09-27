import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { ContentCard } from "@/components/ui/content-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiErrorBox } from "@/components/ui/api-state";
import { getPublicApprenant } from "@/lib/api/public";

type PortfolioPageProps = {
  params: Promise<{ locale: string; id: string }>;
};

export async function generateMetadata({ params }: PortfolioPageProps): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "portfolio" });
  return { title: t("metaTitle") };
}

export default async function PortfolioPage({ params }: PortfolioPageProps) {
  const { locale, id } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("portfolio");

  try {
    const apprenant = await getPublicApprenant(id);

    return (
      <PublicPageLayout locale={locale}>
        <PageHeader
          title={apprenant.displayName}
          description={t("score", { score: apprenant.score })}
          variant="highlight"
        />
        <div className="mx-auto max-w-3xl space-y-6 px-4 pb-16 sm:px-6">
          <ContentCard accent="highlight">
            <h2 className="font-semibold text-highlight-500">{t("validatedSkills")}</h2>
            <p className="mt-2 text-sm text-text-muted">Profil public — détails via compte connecté.</p>
          </ContentCard>
        </div>
      </PublicPageLayout>
    );
  } catch (error) {
    return (
      <PublicPageLayout locale={locale}>
        <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
          <ApiErrorBox error={error} />
        </div>
      </PublicPageLayout>
    );
  }
}
