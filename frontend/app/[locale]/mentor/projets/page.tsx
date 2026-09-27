import { getTranslations, setRequestLocale } from "next-intl/server";
import { TakeProjectButton } from "@/components/mentor/take-project-button";
import { MatchScoreBadge } from "@/components/ui/match-score-badge";
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

        <h2 className="mb-2 text-lg font-semibold text-text-primary">Projets disponibles</h2>
        <p className="mb-4 text-sm text-text-muted">
          Projets publiés par les clients, pas encore pris en charge. Cliquez sur « Prendre en charge »
          pour les ajouter à « Mes projets ».
        </p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {available.length === 0 ? (
            <ApiEmptyState
              message="Aucun projet publié pour le moment. Le client doit créer un projet puis cliquer « Publier le projet » sur sa page détail."
            />
          ) : (
            available.map((project) => (
              <ContentCard key={project.id} accent="primary">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <h3 className="font-semibold text-text-primary">{project.title}</h3>
                  {project.matchScore != null && (
                    <MatchScoreBadge score={project.matchScore} size="sm" />
                  )}
                </div>
                <p className="mt-2 line-clamp-3 text-sm text-text-muted">{project.description}</p>
                <p className="mt-2 text-xs text-text-muted">Client : {project.client.displayName}</p>
                {project.requiredSkills.length > 0 && (
                  <p className="mt-2 text-xs text-text-muted">
                    Compétences requises : {project.requiredSkills.join(", ")}
                  </p>
                )}
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
