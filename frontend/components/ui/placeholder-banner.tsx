type PlaceholderBannerProps = {
  message: string;
  className?: string;
};

export function PlaceholderBanner({
  message,
  className = "mt-6",
}: PlaceholderBannerProps) {
  return (
    <div
      className={`rounded-lg border border-dashed border-primary-600/40 bg-primary-600/5 px-4 py-3 text-sm text-text-muted ${className}`}
    >
      {message}
    </div>
  );
}
