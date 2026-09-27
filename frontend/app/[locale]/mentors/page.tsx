import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { ContentCard } from "@/components/ui/content-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiErrorBox, ApiEmptyState } from "@/components/ui/api-state";
import { Link } from "@/i18n/navigation";
import { getPublicMentors } from "@/lib/api/public";

type MentorsPageProps = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: MentorsPageProps): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "mentors" });
  return { title: t("metaTitle") };
}

export default async function MentorsPage({ params }: MentorsPageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("mentors");

  try {
    const mentors = await getPublicMentors();

    return (
      <PublicPageLayout locale={locale}>
        <PageHeader title={t("title")} description={t("subtitle")} variant="primary" />
        <div className="mx-auto grid max-w-6xl gap-4 px-4 pb-16 sm:grid-cols-2 lg:grid-cols-3 sm:px-6">
          {mentors.length === 0 ? (
            <ApiEmptyState message="Aucun mentor disponible pour le moment." />
          ) : (
            mentors.map((mentor) => (
              <ContentCard key={mentor.id} accent="accent">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h2 className="font-semibold text-text-primary">{mentor.displayName}</h2>
                    {mentor.isCertified && (
                      <p className="mt-1 text-xs text-primary-600">Certifié</p>
                    )}
                  </div>
                  <span className="rounded-md bg-highlight-500/20 px-2 py-1 text-xs font-medium text-highlight-500">
                    {t("score", { score: mentor.score })}
                  </span>
                </div>
                <Link
                  href={`/mentors/${mentor.id}`}
                  className="mt-4 inline-block text-sm font-medium text-primary-600 hover:text-primary-800"
                >
                  {t("viewProfile")}
                </Link>
              </ContentCard>
            ))
          )}
        </div>
      </PublicPageLayout>
    );
  } catch (error) {
    return (
      <PublicPageLayout locale={locale}>
        <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
          <ApiErrorBox error={error} />
        </div>
      </PublicPageLayout>
    );
  }
}
