import { getTranslations, setRequestLocale } from "next-intl/server";
import { ApprenantOnboardingForm } from "@/components/onboarding/apprenant-onboarding-form";
import { ContentCard } from "@/components/ui/content-card";
import { PageContainer } from "@/components/ui/page-container";
import { PageHeader } from "@/components/ui/page-header";
import { ApiErrorBox } from "@/components/ui/api-state";
import { getAccount } from "@/lib/api/account";
import { requireRole } from "@/lib/auth/server";

type PageProps = { params: Promise<{ locale: string }> };

export default async function ApprenantOnboardingPage({ params }: PageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("apprenantPages.onboarding");

  try {
    const { token } = await requireRole(locale, "apprenant");
    const account = await getAccount(token);

    return (
      <PageContainer>
        <PageHeader title={t("title")} description={t("description")} variant="highlight" />
        <ContentCard accent="highlight" className="max-w-xl shadow-sm">
          <p className="mb-4 text-sm text-text-muted">
            Bienvenue {account.displayName}. Confirmez vos compétences pour personnaliser les
            missions proposées.
          </p>
          <ApprenantOnboardingForm
            initialSkills={account.apprenantProfile?.skills ?? []}
            initialCareerGoal={account.apprenantProfile?.careerGoal ?? ""}
          />
        </ContentCard>
      </PageContainer>
    );
  } catch (error) {
    return <ApiErrorBox error={error} />;
  }
}
