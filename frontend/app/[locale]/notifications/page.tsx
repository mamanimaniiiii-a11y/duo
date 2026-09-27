import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { ContentCard } from "@/components/ui/content-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiEmptyState, ApiErrorBox } from "@/components/ui/api-state";
import { getNotifications } from "@/lib/api/common";
import { requireAuth } from "@/lib/auth/server";

type NotificationsPageProps = { params: Promise<{ locale: string }> };

export async function generateMetadata({
  params,
}: NotificationsPageProps): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "notifications" });
  return { title: t("metaTitle") };
}

export default async function NotificationsPage({ params }: NotificationsPageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("notifications");

  try {
    const { token } = await requireAuth(locale);
    const notifications = await getNotifications(token);

    return (
      <PublicPageLayout locale={locale}>
        <PageHeader title={t("title")} description={t("subtitle")} variant="primary" />
        <div className="mx-auto max-w-4xl space-y-3 px-4 pb-16 sm:px-6">
          {notifications.length === 0 ? (
            <ApiEmptyState message={t("empty")} />
          ) : (
            notifications.map((notification) => (
              <ContentCard key={notification.id} accent="highlight">
                <p className="font-medium text-text-primary">{notification.title}</p>
                <p className="mt-1 text-sm text-text-muted">{notification.body}</p>
                <p className="mt-2 text-xs text-text-muted">
                  {notification.isRead ? "Lu" : "Non lu"} · {notification.createdAt}
                </p>
              </ContentCard>
            ))
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
