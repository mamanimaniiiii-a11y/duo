import { getTranslations, setRequestLocale } from "next-intl/server";
import { ProjectCreateForm } from "@/components/client/project-create-form";
import { PageHeader } from "@/components/ui/page-header";
import { ApiErrorBox } from "@/components/ui/api-state";
import { getPublicCategories } from "@/lib/api/public";
import { requireRole } from "@/lib/auth/server";

type PageProps = { params: Promise<{ locale: string }> };

export default async function NewClientProjectPage({ params }: PageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("client.newProject");

  try {
    await requireRole(locale, "client");
    const categories = await getPublicCategories();

    return (
      <div className="mx-auto w-full max-w-6xl min-w-0">
        <PageHeader title={t("title")} description={t("description")} variant="primary" />
        <ProjectCreateForm categories={categories.filter((c) => c.isActive)} />
      </div>
    );
  } catch (error) {
    return <ApiErrorBox error={error} />;
  }
}
