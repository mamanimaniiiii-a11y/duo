import { Link } from "@/i18n/navigation";
import { ContentCard } from "@/components/ui/content-card";
import { PageContainer } from "@/components/ui/page-container";
import { PageHeader } from "@/components/ui/page-header";

type StatItem = {
  label: string;
  value: string | number;
  accent?: "primary" | "accent" | "highlight" | "none";
};

type QuickAction = {
  href: string;
  label: string;
};

type RoleDashboardViewProps = {
  title: string;
  description: string;
  variant: "default" | "primary" | "accent" | "highlight" | "dark";
  stats: StatItem[];
  actions: QuickAction[];
  sectionTitle?: string;
  sectionContent?: React.ReactNode;
};

export function RoleDashboardView({
  title,
  description,
  variant,
  stats,
  actions,
  sectionTitle,
  sectionContent,
}: RoleDashboardViewProps) {
  return (
    <PageContainer>
      <PageHeader title={title} description={description} variant={variant} />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map((stat) => (
          <ContentCard key={stat.label} accent={stat.accent ?? "primary"} className="shadow-sm">
            <p className="text-sm font-medium text-text-muted">{stat.label}</p>
            <p className="mt-2 text-3xl font-semibold tracking-tight text-text-primary">
              {stat.value}
            </p>
          </ContentCard>
        ))}
      </div>

      {actions.length > 0 && (
        <ContentCard accent="none" className="mt-6 shadow-sm">
          <h2 className="text-base font-semibold text-text-primary">Actions rapides</h2>
          <div className="mt-4 flex flex-wrap gap-2">
            {actions.map((action) => (
              <Link
                key={action.href}
                href={action.href}
                className="inline-flex rounded-lg border border-border bg-white px-4 py-2 text-sm font-medium text-text-primary transition-colors hover:bg-surface-50"
              >
                {action.label}
              </Link>
            ))}
          </div>
        </ContentCard>
      )}

      {sectionContent && (
        <ContentCard accent="none" className="mt-6 shadow-sm">
          {sectionTitle && (
            <h2 className="mb-4 text-base font-semibold text-text-primary">{sectionTitle}</h2>
          )}
          {sectionContent}
        </ContentCard>
      )}
    </PageContainer>
  );
}
