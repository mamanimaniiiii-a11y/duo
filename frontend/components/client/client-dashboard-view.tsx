import { ContentCard } from "@/components/ui/content-card";
import { PageHeader } from "@/components/ui/page-header";
import type { DashboardStats } from "@/lib/types/dashboard";

type ClientDashboardViewProps = {
  title: string;
  description: string;
  stats: DashboardStats;
};

const STAT_CARDS = [
  {
    key: "activeProjects" as const,
    label: "Projets actifs",
    accent: "primary" as const,
    chip: "bg-primary-600/10 text-primary-600",
  },
  {
    key: "completedProjects" as const,
    label: "Projets terminés",
    accent: "accent" as const,
    chip: "bg-primary-800/10 text-primary-800",
  },
  {
    key: "unreadMessages" as const,
    label: "Messages non lus",
    accent: "highlight" as const,
    chip: "bg-highlight-500/15 text-highlight-500",
  },
  {
    key: "unreadNotifications" as const,
    label: "Notifications",
    accent: "primary" as const,
    chip: "bg-primary-800/10 text-primary-800",
  },
];

export function ClientDashboardView({
  title,
  description,
  stats,
}: ClientDashboardViewProps) {
  return (
    <div className="mx-auto w-full max-w-6xl">
      <PageHeader title={title} description={description} variant="primary" />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {STAT_CARDS.map((card) => (
          <ContentCard key={card.key} accent={card.accent} className="shadow-md">
            <div className="flex items-start justify-between gap-3">
              <p className="text-sm font-medium text-text-muted">{card.label}</p>
              <span
                className={`rounded-md px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${card.chip}`}
              >
                Live
              </span>
            </div>
            <p className="mt-3 text-3xl font-semibold tracking-tight text-text-primary">
              {stats[card.key]}
            </p>
          </ContentCard>
        ))}
      </div>

      <ContentCard accent="accent" className="mt-6 shadow-md">
        <h2 className="text-lg font-semibold text-text-primary">Vue d&apos;ensemble</h2>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-text-muted">
          Vos indicateurs proviennent directement de l&apos;API client. Créez un nouveau
          projet ou consultez vos livrables depuis le menu latéral.
        </p>
      </ContentCard>
    </div>
  );
}
