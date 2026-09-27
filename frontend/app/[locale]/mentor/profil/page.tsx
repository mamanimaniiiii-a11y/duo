import { getTranslations, setRequestLocale } from "next-intl/server";
import { MentorProfileForm } from "@/components/profile/mentor-profile-form";
import { ContentCard } from "@/components/ui/content-card";
import { PageContainer } from "@/components/ui/page-container";
import { PageHeader } from "@/components/ui/page-header";
import { ApiErrorBox } from "@/components/ui/api-state";
import { getAccount } from "@/lib/api/account";
import { getPublicCategories } from "@/lib/api/public";
import { requireRole } from "@/lib/auth/server";
import type { AppLocale } from "@/i18n/routing";

type PageProps = { params: Promise<{ locale: string }> };

export default async function MentorProfilePage({ params }: PageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("mentorPages.profile");

  try {
    const { token } = await requireRole(locale, "mentor");
    const [account, categories] = await Promise.all([
      getAccount(token),
      getPublicCategories(),
    ]);

    return (
      <PageContainer>
        <PageHeader title={t("title")} description={t("description")} variant="accent" />
        <ContentCard accent="accent" className="max-w-xl shadow-sm">
          <MentorProfileForm
            locale={locale as AppLocale}
            categories={categories.filter((c) => c.isActive)}
            initialBio={account.mentorProfile?.bio ?? ""}
            initialCategoryIds={account.mentorProfile?.serviceCategoryIds ?? []}
          />
        </ContentCard>
      </PageContainer>
    );
  } catch (error) {
    return <ApiErrorBox error={error} />;
  }
}
