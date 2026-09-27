import { getTranslations, setRequestLocale } from "next-intl/server";
import { AssignMentorButton } from "@/components/client/assign-mentor-button";
import { PublishProjectButton } from "@/components/client/publish-project-button";
import { MatchScoreBadge } from "@/components/ui/match-score-badge";
import { ContentCard } from "@/components/ui/content-card";
import { PageHeader } from "@/components/ui/page-header";
import { ApiErrorBox } from "@/components/ui/api-state";
import { getClientProject, getClientProjectMentorMatches } from "@/lib/api/roles/client";
import { requireRole } from "@/lib/auth/server";

type PageProps = { params: Promise<{ locale: string; id: string }> };

export default async function ClientProjectDetailPage({ params }: PageProps) {
  const { locale, id } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("client.projectDetail");

  try {
    const { token } = await requireRole(locale, "client");
    const project = await getClientProject(token, id);
    const mentorMatches =
      project.status === "published" && !project.mentor
        ? await getClientProjectMentorMatches(token, id)
        : project.requiredSkills.length > 0 && project.status === "draft" && !project.mentor
          ? await getClientProjectMentorMatches(token, id)
          : [];

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
            {project.requiredSkills.length > 0 && (
              <p className="mt-4 text-sm">
                Compétences mentor requises : {project.requiredSkills.join(", ")}
              </p>
            )}
            {project.status === "draft" && (
              <div className="mt-6 border-t border-border pt-4">
                <PublishProjectButton projectId={project.id} />
              </div>
            )}
            {project.status === "published" && (
              <p className="mt-4 rounded-lg bg-surface-50 px-3 py-2 text-sm text-text-muted">
                Projet publié. Choisissez un mentor dans la liste ci-dessous.
              </p>
            )}
            {project.status === "assigned" && project.mentor && (
              <div className="mt-4 rounded-lg bg-green-50 px-3 py-2 text-sm text-green-800">
                <p>
                  Mentor assigné : {project.mentor.displayName} (@{project.mentor.username})
                </p>
                {project.mentorMatchScore != null && (
                  <div className="mt-2">
                    <MatchScoreBadge score={project.mentorMatchScore} size="sm" />
                  </div>
                )}
              </div>
            )}
          </ContentCard>
          <ContentCard accent="accent">
            <h2 className="font-semibold text-primary-600">Mentor</h2>
            <p className="mt-2 text-sm text-text-muted">
              {project.mentor?.displayName ?? "Non assigné"}
            </p>
            {project.mentorMatchScore != null && (
              <div className="mt-3">
                <MatchScoreBadge score={project.mentorMatchScore} />
              </div>
            )}
          </ContentCard>
          {mentorMatches.length > 0 && (
            <ContentCard accent="accent" className="lg:col-span-2">
              <h2 className="font-semibold text-primary-600">
                {project.status === "draft"
                  ? "Aperçu du matching"
                  : "Tous les mentors (classés par compatibilité)"}
              </h2>
              <p className="mt-1 text-sm text-text-muted">
                Matching = 50 % compétences + 50 % score mentor (sur 100).
              </p>
              <ul className="mt-4 space-y-2 text-sm">
                {mentorMatches.map((match) => (
                  <li
                    key={match.mentor.id}
                    className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-border bg-surface-50 px-3 py-3"
                  >
                    <div>
                      <p className="font-medium text-text-primary">
                        {match.mentor.displayName} (@{match.mentor.username})
                      </p>
                      <p className="mt-1 text-xs text-text-muted">
                        Compétences : {match.mentor.skills.join(", ") || "—"}
                      </p>
                      <p className="mt-1 text-xs text-text-muted">
                        Skills {match.skillsMatchPercent}% · Score mentor {match.mentorScore} ·{" "}
                        {match.skillsOverlap} compétence(s) commune(s)
                      </p>
                    </div>
                    {project.status === "published" ? (
                      <AssignMentorButton projectId={project.id} match={match} />
                    ) : (
                      <MatchScoreBadge score={match.matchScore} size="sm" />
                    )}
                  </li>
                ))}
              </ul>
            </ContentCard>
          )}

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
