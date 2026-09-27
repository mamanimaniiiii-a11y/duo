import { getTranslations, setRequestLocale } from "next-intl/server";
import { ContentCard } from "@/components/ui/content-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiEmptyState, ApiErrorBox } from "@/components/ui/api-state";
import { getMentorBoostOptions } from "@/lib/api/roles/mentor";
import { requireRole } from "@/lib/auth/server";
import type { AppLocale } from "@/i18n/routing";

type PageProps = { params: Promise<{ locale: string }> };

export default async function MentorBoostPage({ params }: PageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("mentorPages.boost");
  const appLocale = locale as AppLocale;

  try {
    const { token } = await requireRole(locale, "mentor");
    const options = await getMentorBoostOptions(token);

    return (
      <>
        <PageHeader title={t("title")} description={t("description")} variant="accent" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {options.length === 0 ? (
            <ApiEmptyState message="Aucune option boost disponible." />
          ) : (
            options.map((option) => (
              <ContentCard key={option.id} accent="accent">
                <h3 className="font-semibold text-text-primary">{option.label[appLocale]}</h3>
                <p className="mt-2 text-sm text-text-muted">
                  {option.durationDays} jours · {option.priceDzd} DZD
                </p>
              </ContentCard>
            ))
          )}
        </div>
      </>
    );
  } catch (error) {
    return <ApiErrorBox error={error} />;
  }
}
