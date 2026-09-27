import { getTranslations, setRequestLocale } from "next-intl/server";
import { RoleDashboardView } from "@/components/dashboard/role-dashboard-view";
import { ApiErrorBox } from "@/components/ui/api-state";
import { getClientDashboard } from "@/lib/api/roles/client";
import { requireRole } from "@/lib/auth/server";

type PageProps = { params: Promise<{ locale: string }> };

export default async function ClientDashboardPage({ params }: PageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("client.dashboard");

  try {
    const { token } = await requireRole(locale, "client");
    const stats = await getClientDashboard(token);

    return (
      <RoleDashboardView
        title={t("title")}
        description={t("description")}
        variant="primary"
        stats={[
          { label: "Projets actifs", value: stats.activeProjects, accent: "primary" },
          { label: "Projets terminés", value: stats.completedProjects, accent: "accent" },
          { label: "Messages non lus", value: stats.unreadMessages, accent: "highlight" },
          { label: "Notifications", value: stats.unreadNotifications, accent: "primary" },
        ]}
        actions={[
          { href: "/client/projets/nouveau", label: "Nouveau projet" },
          { href: "/client/projets", label: "Mes projets" },
          { href: "/messages", label: "Messages" },
          { href: "/notifications", label: "Notifications" },
        ]}
      />
    );
  } catch (error) {
    return <ApiErrorBox error={error} />;
  }
}
