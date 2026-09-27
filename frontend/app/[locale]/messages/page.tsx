import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { PublicPageLayout } from "@/components/layout/public-page-layout";
import { ContentCard } from "@/components/ui/content-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiEmptyState, ApiErrorBox } from "@/components/ui/api-state";
import { getMessages } from "@/lib/api/common";
import { requireAuth } from "@/lib/auth/server";

type MessagesPageProps = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: MessagesPageProps): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "messages" });
  return { title: t("metaTitle") };
}

export default async function MessagesPage({ params }: MessagesPageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("messages");

  try {
    const { token } = await requireAuth(locale);
    const messages = await getMessages(token);

    return (
      <PublicPageLayout locale={locale}>
        <PageHeader title={t("title")} description={t("subtitle")} variant="primary" />
        <div className="mx-auto max-w-4xl space-y-3 px-4 pb-16 sm:px-6">
          {messages.length === 0 ? (
            <ApiEmptyState message={t("empty")} />
          ) : (
            messages.map((message) => (
              <ContentCard key={message.id} accent="primary">
                <p className="text-sm text-text-primary">{message.content}</p>
                <p className="mt-2 text-xs text-text-muted">
                  {message.isRead ? "Lu" : "Non lu"} · {message.createdAt}
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
