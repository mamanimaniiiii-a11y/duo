import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { ContentCard } from "@/components/ui/content-card";
import { PageHeader } from "@/components/ui/page-header";

type ForgotPasswordPageProps = {
  params: Promise<{ locale: string }>;
};

export async function generateMetadata({
  params,
}: ForgotPasswordPageProps): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "auth" });
  return { title: t("forgotPassword") };
}

export default async function ForgotPasswordPage({
  params,
}: ForgotPasswordPageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("auth");

  return (
    <PublicPageLayout locale={locale}>
      <div className="mx-auto max-w-lg px-4 py-12">
        <PageHeader
          title={t("forgotPassword")}
          description={t("email")}
          variant="primary"
        />
        <ContentCard accent="primary">
          <input
            type="email"
            className="w-full rounded-lg border border-border bg-surface-50 px-4 py-2.5 outline-none focus:border-primary-600"
            placeholder="vous@exemple.dz"
          />
        </ContentCard>
      </div>
    </PublicPageLayout>
  );
}
