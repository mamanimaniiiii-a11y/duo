import { getTranslations, setRequestLocale } from "next-intl/server";
import { ContentCard } from "@/components/ui/content-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiErrorBox } from "@/components/ui/api-state";
import { getAdminBoostOptions, getAdminPremiumPlans } from "@/lib/api/roles/admin";
import { requireRole } from "@/lib/auth/server";
import type { AppLocale } from "@/i18n/routing";

type PageProps = { params: Promise<{ locale: string }> };

export default async function AdminBoostPremiumPage({ params }: PageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("adminPages.boostPremium");
  const appLocale = locale as AppLocale;

  try {
    const { token } = await requireRole(locale, "admin");
    const [boostOptions, premiumPlans] = await Promise.all([
      getAdminBoostOptions(token),
      getAdminPremiumPlans(token),
    ]);

    return (
      <>
        <PageHeader title={t("title")} description={t("description")} variant="dark" />
        <h2 className="mb-4 text-lg font-semibold">Options Boost</h2>
        <div className="mb-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {boostOptions.map((option) => (
            <ContentCard key={option.id} accent="accent">
              <p className="font-medium text-text-primary">{option.label[appLocale]}</p>
              <p className="mt-2 text-sm text-text-muted">
                {option.durationDays} j · {option.priceDzd} DZD
              </p>
            </ContentCard>
          ))}
        </div>
        <h2 className="mb-4 text-lg font-semibold">Plans Premium</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {premiumPlans.map((plan) => (
            <ContentCard key={plan.id} accent="primary">
              <p className="font-medium text-text-primary">{plan.label[appLocale]}</p>
              <p className="mt-2 text-sm text-text-muted">
                {plan.durationDays} j · {plan.priceDzd} DZD
              </p>
            </ContentCard>
          ))}
        </div>
      </>
    );
  } catch (error) {
    return <ApiErrorBox error={error} />;
  }
}
