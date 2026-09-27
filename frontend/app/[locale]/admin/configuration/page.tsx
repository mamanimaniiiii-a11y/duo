import { getTranslations, setRequestLocale } from "next-intl/server";
import { ContentCard } from "@/components/ui/content-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiEmptyState, ApiErrorBox } from "@/components/ui/api-state";
import { getAdminCategories } from "@/lib/api/roles/admin";
import { requireRole } from "@/lib/auth/server";
import type { AppLocale } from "@/i18n/routing";

type PageProps = { params: Promise<{ locale: string }> };

export default async function AdminConfigurationPage({ params }: PageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("adminPages.configuration");
  const appLocale = locale as AppLocale;

  try {
    const { token } = await requireRole(locale, "admin");
    const categories = await getAdminCategories(token);

    return (
      <>
        <PageHeader title={t("title")} description={t("description")} variant="dark" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {categories.length === 0 ? (
            <ApiEmptyState message="Aucune catégorie configurée." />
          ) : (
            categories.map((category) => (
              <ContentCard key={category.id} accent="primary">
                <p className="font-mono text-xs text-text-muted">{category.slug}</p>
                <p className="mt-1 font-medium text-text-primary">{category.name[appLocale]}</p>
                <p className="mt-2 text-xs text-text-muted">
                  {category.isActive ? "Active" : "Inactive"} · ordre {category.sortOrder}
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
