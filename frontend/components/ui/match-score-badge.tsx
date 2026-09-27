type MatchScoreBadgeProps = {
  score: number;
  size?: "sm" | "md";
};

function scoreTone(score: number): string {
  if (score >= 70) return "bg-green-100 text-green-800 border-green-200";
  if (score >= 40) return "bg-primary-50 text-primary-800 border-primary-200";
  return "bg-amber-50 text-amber-800 border-amber-200";
}

export function MatchScoreBadge({ score, size = "md" }: MatchScoreBadgeProps) {
  const sizeClass = size === "sm" ? "px-2 py-0.5 text-xs" : "px-3 py-1 text-sm";

  return (
    <span
      className={`inline-flex items-center rounded-full border font-semibold ${sizeClass} ${scoreTone(score)}`}
    >
      Matching {score}%
    </span>
  );
}
