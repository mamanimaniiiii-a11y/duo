import { getTranslations, setRequestLocale } from "next-intl/server";
import { ContentCard } from "@/components/ui/content-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiEmptyState, ApiErrorBox } from "@/components/ui/api-state";
import { getAdminUsers } from "@/lib/api/roles/admin";
import { requireRole } from "@/lib/auth/server";

type PageProps = { params: Promise<{ locale: string }> };

export default async function AdminUsersPage({ params }: PageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("adminPages.users");

  try {
    const { token } = await requireRole(locale, "admin");
    const users = await getAdminUsers(token);

    return (
      <>
        <PageHeader title={t("title")} description={t("description")} variant="dark" />
        <div className="space-y-3">
          {users.length === 0 ? (
            <ApiEmptyState message="Aucun utilisateur." />
          ) : (
            users.map((user) => (
              <ContentCard key={user.id} accent="primary">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <p className="font-medium text-text-primary">{user.displayName}</p>
                    <p className="text-sm text-text-muted">{user.email}</p>
                  </div>
                  <p className="text-sm capitalize">{user.role}</p>
                  <p className="text-xs text-text-muted">
                    {user.isActive ? "Actif" : "Inactif"}
                  </p>
                </div>
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
