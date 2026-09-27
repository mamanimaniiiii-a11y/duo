import { getTranslations, setRequestLocale } from "next-intl/server";
import { TakeProjectButton } from "@/components/mentor/take-project-button";
import { EntityCard } from "@/components/data/entity-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiEmptyState, ApiErrorBox } from "@/components/ui/api-state";
import { ContentCard } from "@/components/ui/content-card";
import {
  getMentorAvailableProjects,
  getMentorProjects,
} from "@/lib/api/roles/mentor";
import { requireRole } from "@/lib/auth/server";

type PageProps = { params: Promise<{ locale: string }> };

export default async function MentorProjectsPage({ params }: PageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("mentorPages.projects");

  try {
    const { token } = await requireRole(locale, "mentor");
    const [projects, available] = await Promise.all([
      getMentorProjects(token),
      getMentorAvailableProjects(token),
    ]);

    return (
      <>
        <PageHeader title={t("title")} description={t("description")} variant="accent" />
        <h2 className="mb-4 text-lg font-semibold text-text-primary">Mes projets</h2>
        <div className="mb-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects.length === 0 ? (
            <ApiEmptyState message="Aucun projet pris en charge." />
          ) : (
            projects.map((project) => (
              <EntityCard
                key={project.id}
                href={`/mentor/projets/${project.id}`}
                title={project.title}
                description={project.description}
                meta={`${project.status} · ${project.client.displayName}`}
                accent="accent"
              />
            ))
          )}
        </div>

        <h2 className="mb-4 text-lg font-semibold text-text-primary">Projets disponibles</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {available.length === 0 ? (
            <ApiEmptyState message="Aucun projet disponible." />
          ) : (
            available.map((project) => (
              <ContentCard key={project.id} accent="primary">
                <h3 className="font-semibold text-text-primary">{project.title}</h3>
                <p className="mt-2 line-clamp-3 text-sm text-text-muted">{project.description}</p>
                <p className="mt-2 text-xs text-text-muted">Client : {project.client.displayName}</p>
                <div className="mt-4">
                  <TakeProjectButton projectId={project.id} />
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
