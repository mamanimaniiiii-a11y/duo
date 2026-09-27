import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { ContentCard } from "@/components/ui/content-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiErrorBox } from "@/components/ui/api-state";
import { getPublicMentor } from "@/lib/api/public";

type MentorProfilePageProps = {
  params: Promise<{ locale: string; id: string }>;
};

export async function generateMetadata({ params }: MentorProfilePageProps): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "mentorProfile" });
  return { title: t("metaTitle") };
}

export default async function MentorProfilePage({ params }: MentorProfilePageProps) {
  const { locale, id } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("mentorProfile");

  try {
    const mentor = await getPublicMentor(id);

    return (
      <PublicPageLayout locale={locale}>
        <PageHeader
          title={mentor.displayName}
          description={mentor.isCertified ? t("certified") : undefined}
          variant="accent"
        />
        <div className="mx-auto max-w-3xl space-y-6 px-4 pb-16 sm:px-6">
          <ContentCard accent="accent">
            <h2 className="font-semibold text-primary-600">Score</h2>
            <p className="mt-2 text-2xl font-semibold text-text-primary">{mentor.score}</p>
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
