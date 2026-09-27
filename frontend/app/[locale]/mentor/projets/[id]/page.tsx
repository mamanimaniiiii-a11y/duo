import { getTranslations, setRequestLocale } from "next-intl/server";
import { MentorProjectWorkspace } from "@/components/mentor/mentor-project-workspace";
import { PageHeader } from "@/components/ui/page-header";
import { ApiErrorBox } from "@/components/ui/api-state";
import {
  getAssignableApprenants,
  getMentorProject,
  getMentorProjectEligibleApprenants,
  getMentorProjectPacks,
} from "@/lib/api/roles/mentor";
import { requireRole } from "@/lib/auth/server";

type PageProps = { params: Promise<{ locale: string; id: string }> };

export default async function MentorProjectDetailPage({ params }: PageProps) {
  const { locale, id } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("mentorPages.projectDetail");

  try {
    const { token } = await requireRole(locale, "mentor");
    const [project, eligibleApprenants, assignableApprenants, packs] = await Promise.all([
      getMentorProject(token, id),
      getMentorProjectEligibleApprenants(token, id),
      getAssignableApprenants(token),
      getMentorProjectPacks(token, id),
    ]);

    return (
      <>
        <PageHeader title={project.title} description={t("description")} variant="primary" />
        <MentorProjectWorkspace
          project={project}
          eligibleApprenants={eligibleApprenants}
          assignableApprenants={assignableApprenants}
          packs={packs}
        />
      </>
    );
  } catch (error) {
    return <ApiErrorBox error={error} />;
  }
}
