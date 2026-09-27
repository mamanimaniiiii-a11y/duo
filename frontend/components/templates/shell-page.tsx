import { getTranslations } from "next-intl/server";
import { ContentCard } from "@/components/ui/content-card";
import { PageHeader } from "@/components/ui/page-header";
import { PlaceholderBanner } from "@/components/ui/placeholder-banner";

type ShellPageProps = {
  namespace: string;
  variant?: "default" | "primary" | "accent" | "highlight" | "dark";
  accent?: "primary" | "accent" | "highlight" | "none";
};

export async function ShellPage({
  namespace,
  variant = "primary",
  accent = "primary",
}: ShellPageProps) {
  const t = await getTranslations(namespace);
  const tCommon = await getTranslations("common");

  return (
    <>
      <PageHeader
        title={t("title")}
        description={t("description")}
        variant={variant}
      />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <ContentCard accent={accent}>
          <p className="text-sm font-medium text-text-primary">{t("title")}</p>
          <p className="mt-1 text-sm text-text-muted">{t("description")}</p>
        </ContentCard>
        <ContentCard accent={accent}>
          <div className="h-20 rounded-lg bg-surface-50" />
        </ContentCard>
        <ContentCard accent={accent}>
          <div className="h-20 rounded-lg bg-surface-50" />
        </ContentCard>
      </div>
      <PlaceholderBanner message={tCommon("comingSoon")} />
    </>
  );
}
