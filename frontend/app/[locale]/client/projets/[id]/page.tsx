import { getTranslations, setRequestLocale } from "next-intl/server";
import { ContentCard } from "@/components/ui/content-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiErrorBox } from "@/components/ui/api-state";
import { getClientProject } from "@/lib/api/roles/client";
import { requireRole } from "@/lib/auth/server";

type PageProps = { params: Promise<{ locale: string; id: string }> };

export default async function ClientProjectDetailPage({ params }: PageProps) {
  const { locale, id } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("client.projectDetail");

  try {
    const { token } = await requireRole(locale, "client");
    const project = await getClientProject(token, id);

    return (
      <>
        <PageHeader title={project.title} description={t("description")} variant="primary" />
        <div className="grid gap-4 lg:grid-cols-2">
          <ContentCard accent="primary">
            <p className="text-sm text-text-muted">{project.description}</p>
            <p className="mt-4 text-sm">Statut : {project.status}</p>
            <p className="text-sm">Progression : {project.progressPercent}%</p>
            {project.budgetDzd != null && (
              <p className="text-sm">Budget : {project.budgetDzd} DZD</p>
            )}
          </ContentCard>
          <ContentCard accent="accent">
            <h2 className="font-semibold text-primary-600">Mentor</h2>
            <p className="mt-2 text-sm text-text-muted">
              {project.mentor?.displayName ?? "Non assigné"}
            </p>
          </ContentCard>
          <ContentCard accent="highlight">
            <h2 className="font-semibold text-highlight-500">Livrables</h2>
            <ul className="mt-2 space-y-2 text-sm text-text-muted">
              {project.deliverables.map((d) => (
                <li key={d.id}>{d.title} — {d.status}</li>
              ))}
            </ul>
          </ContentCard>
        </div>
      </>
    );
  } catch (error) {
    return <ApiErrorBox error={error} />;
  }
}
