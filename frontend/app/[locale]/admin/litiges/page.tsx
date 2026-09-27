import { getTranslations, setRequestLocale } from "next-intl/server";
import { ContentCard } from "@/components/ui/content-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiEmptyState, ApiErrorBox } from "@/components/ui/api-state";
import { getAdminDisputes } from "@/lib/api/roles/admin";
import { requireRole } from "@/lib/auth/server";

type PageProps = { params: Promise<{ locale: string }> };

export default async function AdminDisputesPage({ params }: PageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("adminPages.disputes");

  try {
    const { token } = await requireRole(locale, "admin");
    const disputes = await getAdminDisputes(token);

    return (
      <>
        <PageHeader title={t("title")} description={t("description")} variant="dark" />
        <div className="space-y-3">
          {disputes.length === 0 ? (
            <ApiEmptyState message="Aucun litige ouvert." />
          ) : (
            disputes.map((dispute) => (
              <ContentCard key={dispute.id} accent="highlight">
                <p className="font-medium text-text-primary">Litige {dispute.id}</p>
                <p className="mt-1 text-sm text-text-muted">Projet : {dispute.projectId}</p>
                <p className="text-sm">Statut : {dispute.status}</p>
                <p className="text-sm text-text-muted">{dispute.reason}</p>
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
