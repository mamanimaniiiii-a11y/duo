import type { ReactNode } from "react";

type ContentCardProps = {
  children: ReactNode;
  className?: string;
  accent?: "primary" | "accent" | "highlight" | "none";
};

const ACCENT_BORDER = {
  primary: "border-s-4 border-s-primary-600",
  accent: "border-s-4 border-s-primary-600",
  highlight: "border-s-4 border-s-highlight-500",
  none: "",
};

export function ContentCard({
  children,
  className = "",
  accent = "primary",
}: ContentCardProps) {
  return (
    <div
      className={`rounded-xl border border-border bg-surface-100 p-5 shadow-sm ${ACCENT_BORDER[accent]} ${className}`}
    >
      {children}
    </div>
  );
}
