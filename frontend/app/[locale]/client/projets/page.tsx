import { getTranslations, setRequestLocale } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { PageHeader } from "@/components/ui/page-header";
import { ApiEmptyState, ApiErrorBox } from "@/components/ui/api-state";
import { EntityCard } from "@/components/data/entity-card";
import { getClientProjects } from "@/lib/api/roles/client";
import { requireRole } from "@/lib/auth/server";
import type { ProjectStatus } from "@/lib/types/common";

const STATUS_LABELS: Record<ProjectStatus, string> = {
  draft: "Brouillon — à publier",
  published: "Publié — en attente d'un mentor",
  assigned: "Assigné à un mentor",
  in_progress: "En cours",
  delivered: "Livré",
  completed: "Terminé",
  cancelled: "Annulé",
};

type PageProps = { params: Promise<{ locale: string }> };

export default async function ClientProjectsPage({ params }: PageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("client.projects");

  try {
    const { token } = await requireRole(locale, "client");
    const projects = await getClientProjects(token);

    return (
      <>
        <PageHeader title={t("title")} description={t("description")} variant="primary" />
        <div className="mb-6">
          <Link
            href="/client/projets/nouveau"
            className="inline-flex rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white"
          >
            Nouveau projet
          </Link>
        </div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects.length === 0 ? (
            <ApiEmptyState message="Aucun projet pour le moment." />
          ) : (
            projects.map((project) => (
              <EntityCard
                key={project.id}
                href={`/client/projets/${project.id}`}
                title={project.title}
                description={project.description}
                meta={`${STATUS_LABELS[project.status] ?? project.status} · ${project.progressPercent}%`}
              />
            ))
          )}
        </div>
      </>
    );
  } catch (error) {
    return <ApiErrorBox error={error} />;
  }
}
