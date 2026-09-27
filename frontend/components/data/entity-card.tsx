import { Link } from "@/i18n/navigation";
import { ContentCard } from "@/components/ui/content-card";

type EntityCardProps = {
  title: string;
  description?: string;
  meta?: string;
  href?: string;
  accent?: "primary" | "accent" | "highlight" | "none";
};

export function EntityCard({
  title,
  description,
  meta,
  href,
  accent = "primary",
}: EntityCardProps) {
  const content = (
    <ContentCard accent={accent} className="h-full shadow-sm transition-shadow hover:shadow-md">
      <h2 className="font-semibold text-text-primary">{title}</h2>
      {description && (
        <p className="mt-2 line-clamp-3 text-sm text-text-muted">{description}</p>
      )}
      {meta && <p className="mt-3 text-xs text-text-muted">{meta}</p>}
    </ContentCard>
  );

  if (href) {
    return (
      <Link href={href} className="block h-full">
        {content}
      </Link>
    );
  }

  return content;
}
