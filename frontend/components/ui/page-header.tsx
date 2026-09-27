type PageHeaderProps = {
  title: string;
  description?: string;
  variant?: "default" | "primary" | "accent" | "highlight" | "dark";
};

const VARIANT_CLASSES = {
  default: "bg-surface-100 border-border text-text-primary",
  primary: "bg-primary-600 border-primary-800 text-white",
  accent: "bg-primary-600 border-primary-800 text-white",
  highlight: "bg-highlight-500 border-highlight-500 text-white",
  dark: "bg-primary-800 border-primary-800 text-white",
};

export function PageHeader({
  title,
  description,
  variant = "primary",
}: PageHeaderProps) {
  const classes = VARIANT_CLASSES[variant];

  return (
    <header
      className={`mb-6 rounded-xl border px-6 py-8 sm:px-8 ${classes}`}
    >
      <h1 className="text-2xl font-semibold sm:text-3xl">{title}</h1>
      {description && (
        <p
          className={`mt-2 max-w-2xl text-base ${
            variant === "default" ? "text-text-muted" : "text-white/85"
          }`}
        >
          {description}
        </p>
      )}
    </header>
  );
}
