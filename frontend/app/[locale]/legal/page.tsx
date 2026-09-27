import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { ContentCard } from "@/components/ui/content-card";
import { PageHeader } from "@/components/ui/page-header";

type LegalPageProps = {
  params: Promise<{ locale: string }>;
};

export async function generateMetadata({
  params,
}: LegalPageProps): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "legal" });
  return { title: t("metaTitle") };
}

export default async function LegalPage({ params }: LegalPageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("legal");

  return (
    <PublicPageLayout locale={locale}>
      <PageHeader title={t("title")} variant="dark" />
      <div className="mx-auto max-w-3xl space-y-6 px-4 py-8 sm:px-6">
        <ContentCard accent="primary">
          <h2 className="text-lg font-semibold text-primary-600">
            {t("termsTitle")}
          </h2>
          <p className="mt-2 text-text-muted">{t("termsBody")}</p>
        </ContentCard>
        <ContentCard accent="accent">
          <h2 className="text-lg font-semibold text-primary-600">
            {t("privacyTitle")}
          </h2>
          <p className="mt-2 text-text-muted">{t("privacyBody")}</p>
        </ContentCard>
      </div>
    </PublicPageLayout>
  );
}
