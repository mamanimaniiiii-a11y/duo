import { getTranslations, setRequestLocale } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { ContentCard } from "@/components/ui/content-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiErrorBox } from "@/components/ui/api-state";
import { getAccount } from "@/lib/api/account";
import { requireRole } from "@/lib/auth/server";

type PageProps = { params: Promise<{ locale: string }> };

export default async function ClientOnboardingPage({ params }: PageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("client.onboarding");

  try {
    const { token } = await requireRole(locale, "client");
    const account = await getAccount(token);

    return (
      <>
        <PageHeader title={t("title")} description={t("description")} variant="primary" />
        <ContentCard accent="primary">
          <p className="text-sm text-text-muted">
            Bienvenue {account.displayName}. Complétez votre profil client depuis le compte.
          </p>
          <Link
            href="/client/dashboard"
            className="mt-4 inline-flex rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white"
          >
            Aller au tableau de bord
          </Link>
        </ContentCard>
      </>
    );
  } catch (error) {
    return <ApiErrorBox error={error} />;
  }
}
