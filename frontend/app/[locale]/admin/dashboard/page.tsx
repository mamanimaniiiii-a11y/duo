import { getTranslations, setRequestLocale } from "next-intl/server";
import { RoleDashboardView } from "@/components/dashboard/role-dashboard-view";
import { ApiErrorBox } from "@/components/ui/api-state";
import { getAdminDashboard } from "@/lib/api/roles/admin";
import { requireRole } from "@/lib/auth/server";

type PageProps = { params: Promise<{ locale: string }> };

export default async function AdminDashboardPage({ params }: PageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("admin.dashboard");

  try {
    const { token } = await requireRole(locale, "admin");
    const stats = await getAdminDashboard(token);

    return (
      <RoleDashboardView
        title={t("title")}
        description={t("description")}
        variant="dark"
        stats={[
          { label: "Utilisateurs", value: stats.totalUsers, accent: "primary" },
          { label: "Mentors", value: stats.totalMentors, accent: "accent" },
          { label: "Litiges", value: stats.openDisputes, accent: "highlight" },
          { label: "Packs en attente", value: stats.pendingPackPurchases, accent: "primary" },
        ]}
        actions={[
          { href: "/admin/utilisateurs", label: "Utilisateurs" },
          { href: "/admin/litiges", label: "Litiges" },
          { href: "/admin/configuration", label: "Configuration" },
          { href: "/admin/boost-premium", label: "Boost premium" },
        ]}
      />
    );
  } catch (error) {
    return <ApiErrorBox error={error} />;
  }
}
