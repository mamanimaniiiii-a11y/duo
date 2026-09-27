import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { ContentCard } from "@/components/ui/content-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiErrorBox } from "@/components/ui/api-state";
import { Link } from "@/i18n/navigation";
import { getAccount } from "@/lib/api/account";
import { requireAuth } from "@/lib/auth/server";

type AccountPageProps = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: AccountPageProps): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "account" });
  return { title: t("metaTitle") };
}

export default async function AccountPage({ params }: AccountPageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("account");

  try {
    const { token } = await requireAuth(locale);
    const account = await getAccount(token);

    return (
      <PublicPageLayout locale={locale}>
        <PageHeader title={t("title")} description={t("subtitle")} variant="dark" />
        <div className="mx-auto grid max-w-4xl gap-4 px-4 pb-16 sm:px-6">
          <ContentCard accent="primary">
            <h2 className="font-medium text-primary-600">{t("profileTab")}</h2>
            <p className="mt-2 text-sm text-text-muted">{account.displayName}</p>
            <p className="text-sm text-text-muted">{account.email}</p>
            <p className="text-sm capitalize text-text-muted">Rôle : {account.role}</p>
          </ContentCard>
          <ContentCard accent="accent">
            <h2 className="font-medium text-primary-600">{t("settingsTab")}</h2>
            <p className="mt-2 text-sm text-text-muted">Locale : {account.locale}</p>
            <p className="text-sm text-text-muted">
              Onboarding : {account.onboardingCompleted ? "terminé" : "en cours"}
            </p>
          </ContentCard>
          {account.scoreBreakdown && (
            <ContentCard accent="highlight">
              <h2 className="font-medium text-highlight-500">{t("reviewsTab")}</h2>
              <p className="mt-2 text-sm text-text-muted">
                Score : {account.scoreBreakdown.total}
              </p>
            </ContentCard>
          )}
          {account.role === "apprenant" && (
            <Link
              href="/apprenant/profil"
              className="inline-flex text-sm font-medium text-highlight-500 hover:underline"
            >
              Modifier mon profil apprenant
            </Link>
          )}
          {account.role === "mentor" && (
            <Link
              href="/mentor/profil"
              className="inline-flex text-sm font-medium text-primary-600 hover:underline"
            >
              Modifier mon profil mentor
            </Link>
          )}
        </div>
      </PublicPageLayout>
    );
  } catch (error) {
    return (
      <PublicPageLayout locale={locale}>
        <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6">
          <ApiErrorBox error={error} />
        </div>
      </PublicPageLayout>
    );
  }
}
